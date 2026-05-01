import streamlit as st

FORMULAS = {
    "📐 Trigonometry": {
        "Pythagorean Identities": [
            (r"\sin^2\theta + \cos^2\theta = 1",       "Core identity"),
            (r"1 + \tan^2\theta = \sec^2\theta",       "Divide by cos²θ"),
            (r"1 + \cot^2\theta = \csc^2\theta",       "Divide by sin²θ"),
        ],
        "Sum & Difference": [
            (r"\sin(a \pm b) = \sin a\cos b \pm \cos a\sin b", ""),
            (r"\cos(a \pm b) = \cos a\cos b \mp \sin a\sin b", ""),
            (r"\tan(a \pm b) = \dfrac{\tan a \pm \tan b}{1 \mp \tan a\tan b}", ""),
        ],
        "Double Angle": [
            (r"\sin 2\theta = 2\sin\theta\cos\theta",        ""),
            (r"\cos 2\theta = \cos^2\theta - \sin^2\theta",  ""),
            (r"\cos 2\theta = 2\cos^2\theta - 1",            ""),
            (r"\cos 2\theta = 1 - 2\sin^2\theta",            ""),
            (r"\tan 2\theta = \dfrac{2\tan\theta}{1-\tan^2\theta}", ""),
        ],
        "Half Angle": [
            (r"\sin\dfrac{\theta}{2} = \pm\sqrt{\dfrac{1-\cos\theta}{2}}", ""),
            (r"\cos\dfrac{\theta}{2} = \pm\sqrt{\dfrac{1+\cos\theta}{2}}", ""),
        ],
        "Reciprocal Identities": [
            (r"\csc\theta = \dfrac{1}{\sin\theta}", ""),
            (r"\sec\theta = \dfrac{1}{\cos\theta}", ""),
            (r"\cot\theta = \dfrac{\cos\theta}{\sin\theta}", ""),
        ],
    },
    "📈 Derivatives": {
        "Basic Rules": [
            (r"\frac{d}{dx}[c] = 0",                           "Constant rule"),
            (r"\frac{d}{dx}[x^n] = nx^{n-1}",                 "Power rule"),
            (r"\frac{d}{dx}[uv] = u'v + uv'",                 "Product rule"),
            (r"\frac{d}{dx}\left[\frac{u}{v}\right] = \frac{u'v - uv'}{v^2}", "Quotient rule"),
            (r"\frac{d}{dx}[f(g(x))] = f'(g(x)) \cdot g'(x)", "Chain rule"),
        ],
        "Common Derivatives": [
            (r"\frac{d}{dx}[\sin x] = \cos x",    ""),
            (r"\frac{d}{dx}[\cos x] = -\sin x",   ""),
            (r"\frac{d}{dx}[\tan x] = \sec^2 x",  ""),
            (r"\frac{d}{dx}[\ln x] = \frac{1}{x}",""),
            (r"\frac{d}{dx}[e^x] = e^x",           ""),
            (r"\frac{d}{dx}[a^x] = a^x \ln a",    ""),
        ],
    },
    "∫ Integrals": {
        "Standard Integrals": [
            (r"\int x^n\,dx = \dfrac{x^{n+1}}{n+1} + C \quad (n \neq -1)", "Power rule"),
            (r"\int \frac{1}{x}\,dx = \ln|x| + C",                          ""),
            (r"\int e^x\,dx = e^x + C",                                       ""),
            (r"\int \sin x\,dx = -\cos x + C",                               ""),
            (r"\int \cos x\,dx = \sin x + C",                                ""),
            (r"\int \sec^2 x\,dx = \tan x + C",                              ""),
            (r"\int \frac{1}{\sqrt{1-x^2}}\,dx = \arcsin x + C",             ""),
            (r"\int \frac{1}{1+x^2}\,dx = \arctan x + C",                    ""),
        ],
        "Key Theorems": [
            (r"\int_a^b f(x)\,dx = F(b) - F(a)",  "Fundamental Theorem of Calculus"),
            (r"\int u\,dv = uv - \int v\,du",       "Integration by Parts"),
        ],
    },
    "🔢 Algebra": {
        "Expansions": [
            (r"(a+b)^2 = a^2 + 2ab + b^2",            ""),
            (r"(a-b)^2 = a^2 - 2ab + b^2",            ""),
            (r"(a+b)(a-b) = a^2 - b^2",                "Difference of squares"),
            (r"(a+b)^3 = a^3 + 3a^2b + 3ab^2 + b^3",  ""),
            (r"a^3 - b^3 = (a-b)(a^2+ab+b^2)",         "Difference of cubes"),
        ],
        "Quadratic Formula": [
            (r"x = \dfrac{-b \pm \sqrt{b^2 - 4ac}}{2a}", "For ax² + bx + c = 0"),
            (r"\Delta = b^2 - 4ac",                        "Discriminant"),
        ],
        "Logarithm Laws": [
            (r"\log(mn) = \log m + \log n",                        "Product"),
            (r"\log\!\left(\dfrac{m}{n}\right) = \log m - \log n", "Quotient"),
            (r"\log(m^n) = n\log m",                                "Power"),
            (r"\log_b a = \dfrac{\ln a}{\ln b}",                    "Change of base"),
        ],
    },
    "🎲 Probability": {
        "Core Rules": [
            (r"P(A \cup B) = P(A) + P(B) - P(A \cap B)", "Addition rule"),
            (r"P(A \cap B) = P(A) \cdot P(B|A)",          "Multiplication rule"),
            (r"P(A|B) = \dfrac{P(B|A)\,P(A)}{P(B)}",      "Bayes' theorem"),
        ],
        "Descriptive Statistics": [
            (r"\bar{x} = \dfrac{1}{n}\sum_{i=1}^n x_i",                      "Mean"),
            (r"\sigma^2 = \dfrac{1}{n}\sum_{i=1}^n (x_i - \bar{x})^2",       "Variance"),
            (r"\sigma = \sqrt{\dfrac{1}{n}\sum_{i=1}^n (x_i-\bar{x})^2}",    "Std deviation"),
        ],
        "Combinatorics": [
            (r"P(n,r) = \dfrac{n!}{(n-r)!}",                      "Permutations"),
            (r"C(n,r) = \binom{n}{r} = \dfrac{n!}{r!(n-r)!}",     "Combinations"),
        ],
    },
    "📊 Linear Algebra": {
        "Matrix Rules": [
            (r"(AB)^T = B^T A^T",              "Transpose of product"),
            (r"\det(AB) = \det(A)\det(B)",     "Determinant product"),
            (r"A^{-1} = \dfrac{1}{\det(A)}\,\text{adj}(A)", "Inverse"),
        ],
        "Eigenvalues": [
            (r"\det(A - \lambda I) = 0",            "Characteristic equation"),
            (r"Av = \lambda v",                      "Eigenvector definition"),
            (r"\text{tr}(A) = \sum \lambda_i",       "Trace = sum of eigenvalues"),
            (r"\det(A) = \prod \lambda_i",           "Det = product of eigenvalues"),
        ],
        "Vectors": [
            (r"\mathbf{u} \cdot \mathbf{v} = |\mathbf{u}||\mathbf{v}|\cos\theta",    "Dot product"),
            (r"|\mathbf{u} \times \mathbf{v}| = |\mathbf{u}||\mathbf{v}|\sin\theta", "Cross product magnitude"),
        ],
    },
}


def render_formula_tab() -> None:
    st.markdown("## 📚 Formula Reference")
    st.markdown("Quick-access LaTeX-rendered formula sheet. Click a topic tab to browse.")

    search = st.text_input("🔍 Search formulas", placeholder="e.g. chain rule, bayes, eigenvalue")

    topic_tabs = st.tabs(list(FORMULAS.keys()))

    for tab, (topic_name, sections) in zip(topic_tabs, FORMULAS.items()):
        with tab:
            for section_title, formulas in sections.items():
                matching = [
                    (latex, note) for latex, note in formulas
                    if not search
                    or search.lower() in latex.lower()
                    or search.lower() in note.lower()
                    or search.lower() in section_title.lower()
                ]
                if not matching:
                    continue
                st.markdown(f"#### {section_title}")
                for latex, note in matching:
                    col1, col2 = st.columns([3, 2])
                    with col1:
                        st.latex(latex)
                    with col2:
                        if note:
                            st.caption(note)
                st.divider()

    if search:
        total = sum(
            1 for sections in FORMULAS.values()
            for formulas in sections.values()
            for latex, note in formulas
            if search.lower() in latex.lower() or search.lower() in note.lower()
        )
        st.info(f"Found **{total}** formula(s) matching '{search}'")