
import streamlit as st









def card(title: str, help_text: str = ""):
    """Render a section card with title and optional help text."""
    st.markdown(
        f"""
        <div class="hub-card">
          <div style="font-weight:600;">{title}</div>
          <div style="color:var(--text-muted); margin-top:4px;">{help_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def hero(title: str, subtitle: str, chips: list[str] | None = None):
    chips_html = ""
    if chips:
        chips_html = '<div class="bi-chip-row">' + "".join(
            f'<span class="bi-chip">{chip}</span>' for chip in chips if chip
        ) + "</div>"
    st.markdown(
        f"""
        <div class="bi-hero">
          <div class="bi-hero-title">{title}</div>
          <div class="bi-hero-subtitle">{subtitle}</div>
          {chips_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def commentary(title: str, bullet_points: list[str]):
    if not bullet_points:
        return
    items = "".join(f"<li>{point}</li>" for point in bullet_points if point)
    st.markdown(
        f"""
        <div class="bi-commentary">
          <div class="bi-commentary-label">{title}</div>
          <ul>{items}</ul>
        </div>
        """,
        unsafe_allow_html=True,
    )




def info_box(title: str, body: str):
    if not title or not body:
        return
    st.markdown(
        f"""
        <div class="bi-audit-card">
          <div class="bi-audit-title">{title}</div>
          <div class="bi-audit-body">{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

























