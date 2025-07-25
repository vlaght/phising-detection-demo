from typing import Any
# this one is the module for quick model showpages
# it's invocations look like a bad-old spaghetti,
# but for my purpose that will do
import streamlit as st
# matplotlib for probability distribution visualization
import matplotlib.pyplot as plt

# for model loading
import joblib

# we still need that one for data serialization

# for inputs randomization
import random

from common import predict_phishing


# Set page config
st.set_page_config(
    page_title="Phishing Detector",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# caching the model to avoid it's every page re-render
@st.cache_resource
def load_model():
    try:
        model = joblib.load("phishing_classifier_light.joblib")
        return model
    except Exception as exc:
        st.error(f"I miserably failed: {exc}")
        return None


# Initial state of form inputs
def initialize_session_state():
    if "google_index" not in st.session_state:
        st.session_state.google_index = False
    if "page_rank" not in st.session_state:
        st.session_state.page_rank = 0
    if "nb_hyperlinks" not in st.session_state:
        st.session_state.nb_hyperlinks = 0
    if "web_traffic" not in st.session_state:
        st.session_state.web_traffic = 0
    if "nb_www" not in st.session_state:
        st.session_state.nb_www = 0
    if "domain_age" not in st.session_state:
        st.session_state.domain_age = 0
    if "longest_word_path" not in st.session_state:
        st.session_state.longest_word_path = 0
    if "ratio_extHyperlinks" not in st.session_state:
        st.session_state.ratio_extHyperlinks = 0.0
    if "ratio_intHyperlinks" not in st.session_state:
        st.session_state.ratio_intHyperlinks = 0.0
    if "phish_hints" not in st.session_state:
        st.session_state.phish_hints = 0


# to play around
def randomize_inputs():
    """Randomize all input values"""
    # I kept original feature names, even though
    # ratio_extHyperlinks and ratio_intHyperlinks are abominations
    # because they are mix snake_case and camelCase;
    # and google_index is confusing because True means 'not indexed'
    st.session_state.google_index = random.choice([True, False])
    st.session_state.page_rank = random.randint(0, 10)
    st.session_state.nb_hyperlinks = random.randint(0, 1000)
    st.session_state.web_traffic = random.randint(0, 1000000)
    st.session_state.nb_www = random.randint(0, 10)
    st.session_state.domain_age = random.randint(0, 10000)
    st.session_state.longest_word_path = random.randint(0, 100)
    st.session_state.ratio_extHyperlinks = round(random.uniform(0.0, 1.0), 3)
    st.session_state.ratio_intHyperlinks = round(random.uniform(0.0, 1.0), 3)
    st.session_state.phish_hints = random.randint(0, 50)


# i'm using concise naming, so comments are not so needed
def validate_inputs(inputs: dict[str, Any]) -> list[str]:
    """Validate input values"""

    # all errors will be accumulated here and returned together
    errors = []

    # validate page_rank (typically 0-10)
    if inputs["page_rank"] < 0:
        errors.append("Page rank must be non-negative")

    # validate nb_hyperlinks, it should be non-negative
    if inputs["nb_hyperlinks"] < 0:
        errors.append("Number of hyperlinks must be non-negative")

    # validate web_traffic
    if inputs["web_traffic"] < 0:
        errors.append("Web traffic must be non-negative")

    # validate nb_www, it should be non-negative
    if inputs["nb_www"] < 0:
        errors.append("Number of www occurrences must be non-negative")

    # validate domain_age, non-negative
    if inputs["domain_age"] < 0:
        errors.append("Domain age must be non-negative")

    # validate longest_word_path, non-negative
    if inputs["longest_word_path"] < 0:
        errors.append("Longest word path must be non-negative")

    # validate ratio_extHyperlinks (should be between 0 and 1)
    if not (0.0 <= inputs["ratio_extHyperlinks"] <= 1.0):
        errors.append("Ratio of external hyperlinks must be between 0.0 and 1.0")

    # validate ratio_intHyperlinks (should be between 0 and 1)
    if not (0.0 <= inputs["ratio_intHyperlinks"] <= 1.0):
        errors.append("Ratio of internal hyperlinks must be between 0.0 and 1.0")

    # validate phish_hints -- non-negative
    if inputs["phish_hints"] < 0:
        errors.append("Phishing hints must be non-negative")

    return errors


def main() -> None:
    initialize_session_state()

    model = load_model()
    if model is None:
        st.error("Model could not be loaded. Please check the logs.")
        st.stop()

    # UI stuff starts here
    st.title("Phishing Detection model interface")

    # 2-columns layout
    left_column, right_column = st.columns([2, 1])

    # context manager here insures that all containing elements
    # will be kept inside of the first column
    with left_column:
        st.markdown("""
            ### How to use:
            1. **Fill in the feature values** below
            2. **Click Predict** to get the result
            3. Optionally, use **Randomize** to randomly fill in the form for quicker testing
            """)
        st.header("Features")

        # input form goes here
        with st.form("prediction_form"):
            # Boolean input
            google_index = st.checkbox(
                "Not indexed by Google",
                value=st.session_state.google_index,
                help="Whether the website is not indexed by Google",
            )

            # I'd like to see inputs in two columns too
            form_left_column, form_right_column = st.columns(2)
            # and again, rendering part of inputs inside the left column
            with form_left_column:
                page_rank = st.number_input(
                    "OpenPageRank rating",
                    min_value=0,
                    max_value=10,
                    value=st.session_state.page_rank,
                    step=1,
                    help="OpenPageRank rating (0-10)",
                )

                nb_hyperlinks = st.number_input(
                    "Hyperlinks count",
                    min_value=0,
                    value=st.session_state.nb_hyperlinks,
                    step=1,
                    help="Total number of hyperlinks on the page",
                )

                web_traffic = st.number_input(
                    "Web traffic",
                    min_value=0,
                    value=st.session_state.web_traffic,
                    step=1,
                    help="Website traffic metrics",
                )

                nb_www = st.number_input(
                    "Number of WWW tokens",
                    min_value=0,
                    value=st.session_state.nb_www,
                    step=1,
                    help="Number of 'www' occurrences in URL",
                )

                domain_age = st.number_input(
                    "Domain age (days)",
                    min_value=0,
                    value=st.session_state.domain_age,
                    step=1,
                    help="Age of the domain in days",
                )
            # and the other part is in the right
            with form_right_column:
                longest_word_path = st.number_input(
                    "Longest word in URL path component",
                    min_value=0,
                    value=st.session_state.longest_word_path,
                    step=1,
                    help="Length of the longest word in link path part",
                )

                ratio_extHyperlinks = st.number_input(
                    "Ratio of external hyperlinks",
                    min_value=0.0,
                    max_value=1.0,
                    value=st.session_state.ratio_extHyperlinks,
                    step=0.001,
                    format="%.3f",
                    help="Ratio of external hyperlinks (0.0 - 1.0)",
                )

                ratio_intHyperlinks = st.number_input(
                    "Ratio of internal hyperlinks",
                    min_value=0.0,
                    max_value=1.0,
                    value=st.session_state.ratio_intHyperlinks,
                    step=0.001,
                    format="%.3f",
                    help="Ratio of internal hyperlinks (0.0 - 1.0)",
                )

                phish_hints = st.number_input(
                    "Phishing hints",
                    min_value=0,
                    value=st.session_state.phish_hints,
                    step=1,
                    help="Number of matches with the following list: ['wp', 'login', 'includes', 'admin', 'content', 'site', 'images', 'js', 'alibaba', 'css', 'myaccount', 'dropbox', 'themes', 'plugins', 'signin', 'view']",
                )

            # buttons; to have them under each of previous columns
            # I have to split the current container in 2-column layout again
            left_button_column, right_button_column = st.columns(2)

            with left_button_column:
                submitted = st.form_submit_button(
                    "Predict",
                    type="primary",
                    use_container_width=True,
                )

            with right_button_column:
                randomize = st.form_submit_button(
                    "Randomize input values",
                    use_container_width=True,
                )

        # handling randomize button press
        if randomize:
            randomize_inputs()
            st.rerun()

        # handling predict button press
        if submitted:
            # collecting inputs
            inputs = {
                "google_index": google_index,
                "page_rank": page_rank,
                "nb_hyperlinks": nb_hyperlinks,
                "web_traffic": web_traffic,
                "nb_www": nb_www,
                "domain_age": domain_age,
                "longest_word_path": longest_word_path,
                "ratio_extHyperlinks": ratio_extHyperlinks,
                "ratio_intHyperlinks": ratio_intHyperlinks,
                "phish_hints": phish_hints,
            }

            #  inputs validation
            errors = validate_inputs(inputs)

            if errors:
                st.error("Please fix the following errors:")
                for error in errors:
                    st.error(f"[x] {error}")
            else:
                # make prediction
                try:
                    prediction, prediction_proba = predict_phishing(model, inputs)
                    # display results in the right column
                    with right_column:
                        st.header("Prediction Result")

                        if prediction == 1:
                            st.error("**PHISHING**")
                        else:
                            st.success("**LEGITIMATE**")

                        # show probability distribution
                        st.subheader("Probability distribution")
                        fig, ax = plt.subplots()
                        ax.pie(
                            prediction_proba,
                            labels=["Legitimate", "Phishing"],
                            autopct="%1.1f%%",
                        )
                        st.pyplot(fig)

                        # show input summary
                        st.subheader("Input Summary")
                        st.json(inputs)

                except Exception as exc:
                    st.error(f"Error making prediction: {exc}")

    with right_column:
        if not submitted:
            st.header("Features Description")
            st.markdown("""
            - **Not indexed by Google**: External-based feature; Is the site NOT indexed by Google?
            - **OpenPageRank rating**: External-based feature; OpenPageRank (https://www.domcop.com/openpagerank/what-is-openpagerank) rating (0-10)
            - **Hyperlinks count**: Content-based feature; Number of links on the page
            - **Web traffic**: External-based feature; Traffic volume metrics from Amazon Alexa
            - **Number of WWW tokens**: URL-based feature; Occurrences of 'www' in URL
            - **Domain age (days)**: External-based feature; How old is the domain in days?
            - **Longest word in URL path component**: URL-based feature; Length of longest word in URL path
            - **Ratio of external hyperlinks**: Content-based feature; Ratio of external links to the total number of links
            - **Ratio of internal hyperlinks**: Content-based feature; Ratio of internal links to the total number of links
            - **Phishing hints**: URL-based feature; Suspicious keyword count
            """)


if __name__ == "__main__":
    main()
