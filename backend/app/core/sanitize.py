"""
XSS / HTML 净化工具 — 对用户输入进行安全过滤。
"""
import html
import re


def sanitize_html(text: str | None) -> str | None:
    """
    对用户输入进行 HTML 实体编码，防止存储型 XSS。
    将 <, >, &, ", ' 转义为对应的 HTML 实体。
    返回净化后的字符串。
    """
    if text is None:
        return None
    return html.escape(text, quote=True)


def sanitize_text(text: str | None) -> str | None:
    """
    对纯文本输入进行净化：HTML 转义 + 去除首尾空白。
    用于 username, note, category_name 等字段。
    """
    if text is None:
        return None
    text = text.strip()
    return html.escape(text, quote=True)


def sanitize_strip(text: str | None) -> str | None:
    """
    对输入去除首尾空白（不转义 HTML，用于 email 等非展示字段）。
    """
    if text is None:
        return None
    text = text.strip()
    # 移除 Unicode 双向控制字符等潜在危险的不可见字符
    text = re.sub(r'[‎‏‪-‮⁦-⁩]', '', text)
    return text
