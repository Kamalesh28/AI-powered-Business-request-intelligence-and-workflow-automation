from pathlib import Path
import json

import plotly.express as px
import streamlit as st

from bri.domain import CHANNELS, DEPARTMENTS, URGENCIES, Category, Priority
from bri.ollama import OllamaAdapter
from bri.reporting import distributions, kpis, to_frame
from bri.seed import seed
from bri.services import RequestService, ReviewService
from bri.storage import Repository
from bri.validation import ValidationError

st.set_page_config(page_title="Business Request Intelligence", layout="wide")
repo = Repository(Path("data") / "business_requests.db")
repo.initialize()
request_service = RequestService(repo)
review_service = ReviewService(repo)

st.title("Business Request Intelligence & Automation")
st.caption("Local demo using synthetic data only. Rules are always retained as an explainable baseline; local AI is optional and validated.")
with st.sidebar:
    st.header("Demo data")
    if st.button("Seed synthetic demo data"):
        st.info(f"Created {seed(repo)} synthetic request(s).")
    page = st.radio("Page", ("Submit request", "Human review", "Reporting"))

if page == "Submit request":
    st.header("Submit a synthetic business request")
    with st.form("intake"):
        title = st.text_input("Title", max_chars=120)
        description = st.text_area("Description", max_chars=4000)
        left, right, third = st.columns(3)
        department = left.selectbox("Department", DEPARTMENTS)
        channel = right.selectbox("Channel", CHANNELS)
        urgency = third.selectbox("Declared urgency", URGENCIES, index=2)
        mode_label = st.radio("Processing mode", ("Rule-based baseline", "Optional local Ollama"), horizontal=True)
        if mode_label == "Optional local Ollama":
            st.caption("Uses only the configured localhost Ollama service. Invalid or unavailable output falls back safely to the rule baseline.")
        submitted = st.form_submit_button("Validate and process")
    if submitted:
        try:
            use_ollama = mode_label == "Optional local Ollama"
            request_id, decision = request_service.submit_and_process(
                {"title": title, "description": description, "department": department, "channel": channel, "declared_urgency": urgency},
                processing_mode="ollama_local" if use_ollama else "rule_based",
                ollama=OllamaAdapter() if use_ollama else None,
            )
            st.success(f"Request {request_id} recorded.")
            st.write({"status": "needs_review" if decision.requires_review else "classified", "category": decision.category, "priority": decision.priority, "confidence": decision.confidence})
            st.json(decision.evidence)
        except ValidationError as exc:
            for message in exc.errors.values():
                st.error(message)

elif page == "Human review":
    st.header("Human review queue")
    queue = repo.requests_for_review()
    if not queue:
        st.info("No requests currently require review.")
    for item in queue:
        with st.expander(f"{item['title']} · confidence {item['confidence']:.0%}", expanded=True):
            st.write(item["description"])
            st.caption(f"Mode: {item['processing_mode']} · processed {item['processed_at_utc']}")
            st.json(json.loads(item["evidence_json"]))
            with st.form(f"review-{item['request_id']}"):
                reviewer = st.text_input("Reviewer name", key=f"reviewer-{item['request_id']}")
                category = st.selectbox("Final category", [x.value for x in Category], index=([x.value for x in Category].index(item["proposed_category"]) if item["proposed_category"] else 0), key=f"category-{item['request_id']}")
                priority = st.selectbox("Final priority", [x.value for x in Priority], index=([x.value for x in Priority].index(item["proposed_priority"]) if item["proposed_priority"] else 2), key=f"priority-{item['request_id']}")
                rationale = st.text_area("Rationale (optional)", key=f"rationale-{item['request_id']}")
                if st.form_submit_button("Confirm or correct decision"):
                    try:
                        review_service.review(item["request_id"], item["processing_run_id"], reviewer, category, priority, rationale, item["proposed_category"], item["proposed_priority"])
                        st.success("Review recorded. Refreshing queue.")
                        st.rerun()
                    except ValidationError as exc:
                        for message in exc.errors.values(): st.error(message)

else:
    st.header("Operational reporting")
    frame = to_frame(repo.report_rows())
    if frame.empty:
        st.info("No stored requests yet. Seed synthetic data or submit one to view reporting.")
    else:
        filter_left, filter_right, filter_status = st.columns(3)
        selected_departments = filter_left.multiselect("Departments", sorted(frame.department.unique()), default=sorted(frame.department.unique()))
        selected_modes = filter_right.multiselect("Processing modes", sorted(frame.processing_mode.dropna().unique()), default=sorted(frame.processing_mode.dropna().unique()))
        selected_statuses = filter_status.multiselect("Statuses", sorted(frame.status.unique()), default=sorted(frame.status.unique()))
        filtered = frame[frame.department.isin(selected_departments) & frame.processing_mode.isin(selected_modes) & frame.status.isin(selected_statuses)]
        metrics = kpis(filtered)
        a, b, c = st.columns(3)
        a.metric("Requests", metrics["requests"])
        b.metric("Review rate", f"{metrics['review_rate']:.1%}")
        c.metric("Correction rate", f"{metrics['correction_rate']:.1%}")
        st.caption("Review rate = reviewed requests / requests. Correction rate = corrected reviewed requests / reviewed requests.")
        charts = distributions(filtered)
        if filtered.empty:
            st.info("No requests match the selected filters.")
        else:
            x, y = st.columns(2)
            x.plotly_chart(px.bar(charts["category"], x="label", y="count", title="Category distribution"), use_container_width=True)
            y.plotly_chart(px.bar(charts["priority"], x="label", y="count", title="Priority distribution"), use_container_width=True)
            st.plotly_chart(px.line(charts["trend"], x="date", y="count", markers=True, title="Request volume by UTC date"), use_container_width=True)
            export = filtered.copy()
            export["submitted_at_utc"] = export["submitted_at_utc"].astype(str)
            st.download_button("Download filtered synthetic report (CSV)", export.to_csv(index=False).encode("utf-8"), "synthetic_business_request_report.csv", "text/csv")
