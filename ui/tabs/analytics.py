import streamlit as st


def render_analytics_tab() -> None:
    from utils.supabase_client import is_enabled, get_analytics
    import plotly.graph_objects as go

    st.markdown("## 📊 Usage Analytics")

    if not is_enabled():
        st.warning("⚠️ Supabase is not configured. Analytics requires database storage.")
        st.info("Add `SUPABASE_URL` and `SUPABASE_KEY` to your `.env` to enable analytics.")
        return

    with st.spinner("Loading analytics…"):
        data = get_analytics()

    if not data:
        st.info("No data yet. Start chatting to see analytics!")
        return

    # ── KPI row ───────────────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    with k1: st.metric("💬 Total Messages",    data.get("total_messages",    0))
    with k2: st.metric("🗂️ Total Sessions",    data.get("total_sessions",    0))
    with k3: st.metric("🧪 Practice Attempts", data.get("practice_total",    0))
    with k4:
        avg = data.get("avg_practice_score", 0)
        st.metric("🎯 Avg Practice Score", f"{avg:.1f}/10" if avg else "N/A")

    st.divider()

    col_left, col_right = st.columns(2)

    # ── Messages per day ──────────────────────────────────────────────
    with col_left:
        st.markdown("#### 📅 Messages Per Day")
        daily = data.get("messages_per_day", [])
        if daily:
            dates  = [row["day"]   for row in daily]
            counts = [row["count"] for row in daily]
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=dates, y=counts,
                mode="lines+markers",
                line=dict(color="#4f98a3", width=2),
                marker=dict(size=6),
                fill="tozeroy",
                fillcolor="rgba(79,152,163,0.15)",
            ))
            fig.update_layout(
                height=280, margin=dict(l=0, r=0, t=10, b=0),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(showgrid=False, color="#797876"),
                yaxis=dict(showgrid=True, gridcolor="#393836", color="#797876"),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.caption("No daily data yet.")

    # ── Model usage donut ─────────────────────────────────────────────
    with col_right:
        st.markdown("#### 🤖 Model Usage")
        model_data = data.get("model_usage", [])
        if model_data:
            labels = [row["model"] for row in model_data]
            values = [row["count"] for row in model_data]
            fig = go.Figure(go.Pie(
                labels=labels, values=values, hole=0.55,
                marker=dict(colors=["#4f98a3","#6daa45","#e8af34","#dd6974","#a86fdf","#fdab43"]),
            ))
            fig.update_layout(
                height=280, margin=dict(l=0, r=0, t=10, b=0),
                paper_bgcolor="rgba(0,0,0,0)",
                legend=dict(font=dict(color="#cdccca"), bgcolor="rgba(0,0,0,0)"),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.caption("No model data yet.")

    col_left2, col_right2 = st.columns(2)

    # ── Role breakdown ────────────────────────────────────────────────
    with col_left2:
        st.markdown("#### 👥 Messages by Role")
        role_data = data.get("role_breakdown", [])
        if role_data:
            roles  = [row["role"]  for row in role_data]
            counts = [row["count"] for row in role_data]
            fig = go.Figure(go.Bar(
                x=roles, y=counts,
                marker_color=["#4f98a3", "#e8af34"],
                text=counts, textposition="outside",
            ))
            fig.update_layout(
                height=260, margin=dict(l=0, r=0, t=10, b=0),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(color="#797876"),
                yaxis=dict(color="#797876", showgrid=False),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.caption("No role data yet.")

    # ── Practice by topic ─────────────────────────────────────────────
    with col_right2:
        st.markdown("#### 🧪 Practice by Topic")
        topic_data = data.get("practice_by_topic", [])
        if topic_data:
            topics = [row["topic"] for row in topic_data]
            counts = [row["count"] for row in topic_data]
            fig = go.Figure(go.Bar(
                x=topics, y=counts,
                marker_color="#4f98a3",
                text=counts, textposition="outside",
            ))
            fig.update_layout(
                height=260, margin=dict(l=0, r=0, t=10, b=0),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(color="#797876", tickangle=-20),
                yaxis=dict(color="#797876", showgrid=False),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.caption("Complete some practice problems to see topic breakdown.")

    # ── Recent sessions table ─────────────────────────────────────────
    st.divider()
    st.markdown("#### 🕘 Recent Sessions")
    recent = data.get("recent_sessions", [])
    if recent:
        import pandas as pd
        df = pd.DataFrame(recent)
        df.columns = ["Session ID", "Messages", "Date"]
        df["Session ID"] = df["Session ID"].apply(lambda x: x[:8] + "…")
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.caption("No sessions yet.")