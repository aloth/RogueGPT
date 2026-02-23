import streamlit as st
from openai import OpenAI, AzureOpenAI
from openai import APIConnectionError, RateLimitError, AuthenticationError, APIError
import json
import re
import itertools
from datetime import datetime

import core

__name__ = "RogueGPT"
__version__ = "1.1.0"
__author__ = "Alexander Loth"
__email__ = "Alexander.Loth@microsoft.com"
__research_paper__ = "https://arxiv.org/abs/2404.03021"
__report_a_bug__ = "https://github.com/aloth/RogueGPT/issues"


def generate_fragment(prompt: str, base_url: str, api_key: str, api_type: str, api_version: str = None, model: str = None) -> str:
    """
    Generates a news fragment using OpenAI's or Azure OpenAI's GPT model and returns the generated response.
    """
    client = None
    try:
        if api_type == "OpenAI":
            client = OpenAI(base_url=base_url, api_key=api_key)
        elif api_type == "AzureOpenAI":
            client = AzureOpenAI(api_key=api_key, api_version=api_version, azure_endpoint=base_url)
        else:
            raise ValueError("Invalid API type. Must be either 'OpenAI' or 'AzureOpenAI'.")

        stream = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )
        generated_response = st.write_stream(stream)
        return generated_response

    except APIConnectionError as e:
        st.error(f"Failed to connect to the API: {e}")
    except RateLimitError as e:
        st.error(f"API request exceeded rate limit: {e}")
    except AuthenticationError as e:
        st.error(f"API authentication failed (check your API key): {e}")
    except APIError as e:
        st.error(f"The API returned an error: {e}")
    except ValueError as e:
        st.error(str(e))
    except Exception as e:
        st.error(f"An unexpected error occurred during fragment generation: {str(e)}")

    return ""


def _save_fragment_ui(fragment: dict) -> None:
    """Save a fragment via core and show status in Streamlit."""
    try:
        result = core.save_fragment(fragment, strict_model=False)
        st.success(f"Fragment saved (ID: {result['fragment_id']})")
        if result["warnings"]:
            for w in result["warnings"]:
                st.warning(w)
    except core.ValidationError as e:
        st.error(f"Validation error: {e}")
    except Exception as e:
        st.error(f"Error saving fragment: {str(e)}")


def render_ui(component_dict: dict, key_prefix: str = "") -> dict:
    """Dynamically renders UI components based on the configuration."""
    user_selections = {}
    for key, value in component_dict.items():
        if isinstance(value, dict):
            selected_option = st.selectbox(f'Choose {key}', list(value.keys()))
            user_selections[key] = selected_option
            nested_dict = value[selected_option]
            for nested_key, nested_value in nested_dict.items():
                if isinstance(nested_value, list):
                    selected_nested_options = st.multiselect(f'Choose {nested_key}', nested_value, default=nested_value)
                    user_selections[f"{nested_key}"] = selected_nested_options
        elif isinstance(value, list):
            selected_options = st.multiselect(f'Choose {key}', value, default=value)
            user_selections[key] = selected_options
    return user_selections


def collect_keys(component_dict: dict, collected_keys: list = []) -> list:
    """Recursively collects all keys from nested dictionaries."""
    for key, value in component_dict.items():
        collected_keys.append(key)
        if isinstance(value, dict):
            for sub_key in value.keys():
                collect_keys(value[sub_key], collected_keys)
    return collected_keys


def fix_structure(selections: dict) -> dict:
    """Ensures all selections are in list form."""
    corrected_selections = {}
    for key, value in selections.items():
        if isinstance(value, list):
            corrected_selections[key] = value
        else:
            corrected_selections[key] = [value]
    return corrected_selections


def manual_data_entry_ui() -> None:
    """Renders UI for manual data entry of news fragments."""
    import uuid
    fragment_id = uuid.uuid4().hex
    st.header("Input News Details")

    st.text_input("Fragment ID", value=fragment_id, disabled=True)

    content = st.text_area("Content")
    origin = st.selectbox("Origin", ["Human", "Machine"])
    if origin == "Human":
        human_outlet = st.text_input("Publishing Outlet Name")
        human_url = st.text_input("URL of News Source")
        machine_model = ""
        machine_prompt = ""
    else:
        human_outlet = ""
        human_url = ""
        machine_model = st.text_input("Generative AI Model")
        machine_prompt = st.text_area("Prompt")

    language = st.selectbox("Language", ["en", "de", "fr", "es"])
    is_fake = st.checkbox("Is this fake news?")

    submit_button = st.button("Submit")

    if submit_button:
        fragment = {
            "FragmentID": fragment_id,
            "Content": content,
            "Origin": origin,
            "HumanOutlet": human_outlet,
            "HumanURL": human_url,
            "MachineModel": machine_model,
            "MachinePrompt": machine_prompt,
            "ISOLanguage": language,
            "IsFake": is_fake,
            "IngestedVia": "ui",
        }
        _save_fragment_ui(fragment)
        st.rerun()


def automatic_news_generation_ui() -> None:
    """Renders UI for automatic news generation."""
    st.header("Automatic News Generation")
    st.subheader("Prompt")

    config = core.load_config()
    prompt_template = config["PromptTemplate"]
    generator_url = config["GeneratorURL"]
    generator_api_key = config["GeneratorAPIKey"]
    generator_api_type = config["GeneratorAPIType"]
    generator_api_version = config["GeneratorAPIVersion"]
    generator_model = config["GeneratorModel"]

    components = config["Components"]
    all_possible_keys = collect_keys(components)

    placeholders = re.findall(r"\[\[(.*?)\]\]", prompt_template)
    uncovered_placeholders = [ph for ph in placeholders if ph not in all_possible_keys]

    user_prompt_template = st.text_input("Prompt Template", prompt_template)

    user_selections = render_ui(components)

    for placeholder in uncovered_placeholders:
        user_input = st.text_area(f"Enter values for {placeholder} (each line is a value)", key=f"placeholder_{placeholder}")
        user_input_options = user_input.split("\n")
        user_selections[placeholder] = user_input_options

    prompt = prompt_template
    for placeholder, selections in user_selections.items():
        placeholder_key = f"[[{placeholder}]]"
        selection_text = selections[0] if isinstance(selections, list) and selections else selections
        prompt = prompt.replace(placeholder_key, selection_text)

    st.write("Prompt Preview:", prompt)

    st.subheader("Generator")
    user_generator_url = st.text_input("Generator URL", generator_url)
    user_generator_api_key = st.text_input("Generator API Key", generator_api_key)
    user_generator_api_type = st.selectbox("Generator API Type", generator_api_type)
    user_generator_api_version = st.selectbox("Generator API Version", generator_api_version)
    user_generator_model = st.selectbox("Generator Model", generator_model)

    st.subheader("Meta data")
    user_is_fakenews = st.checkbox("Mark this as fake news?")

    if st.button("Generate"):
        iter_selections = fix_structure(user_selections)
        st.write(iter_selections)
        keys, values = zip(*iter_selections.items())
        combinations = [dict(zip(keys, v)) for v in itertools.product(*values)]

        for i, combination in enumerate(combinations):
            prompt_filled = prompt_template
            for key, value in combination.items():
                prompt_filled = prompt_filled.replace(f"[[{key}]]", value)

            st.write("Using prompt: ", prompt_filled)

            generated_fragment = generate_fragment(
                prompt=prompt_filled,
                base_url=user_generator_url,
                api_key=user_generator_api_key,
                api_type=user_generator_api_type,
                api_version=user_generator_api_version,
                model=user_generator_model
            )

            combination["FragmentID"] = __import__("uuid").uuid4().hex
            combination["Content"] = generated_fragment
            combination["Origin"] = "Machine"
            combination["MachineModel"] = user_generator_model
            combination["MachinePrompt"] = prompt_filled
            combination["IsFake"] = user_is_fakenews
            combination["IngestedVia"] = "ui"

            _save_fragment_ui(combination)
            st.markdown("---")


# ─── Main UI ──────────────────────────────────────────────────────────

st.title("RogueGPT: News Ingestion")

st.markdown("*Disclaimer:* [RogueGPT](https://github.com/aloth/RogueGPT/) is part of the [JudgeGPT research project](https://github.com/aloth/JudgeGPT/).")
st.markdown("Learn more about the impact of Generative AI on fake news through our [open access paper](" + __research_paper__ + ").")

tab_generator, tab_manual = st.tabs(["Generator", "Manual Data Entry"])

with tab_generator:
    automatic_news_generation_ui()

with tab_manual:
    manual_data_entry_ui()
