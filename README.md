# RogueGPT - (Fake) News Generator

RogueGPT is a research project focused on exploring the boundaries of generative AI in the context of (fake) news fragment generation. This early work-in-progress version is designed to create machine-generated news content, aiming to challenge perceptions and spark discussions on the authenticity of digital content.

If you're curious to explore some of the generated (fake) news by RogueGPT and want to participate in evaluating the authenticity of these news pieces, we warmly invite you to join our interactive survey at [https://judgegpt.streamlit.app/](https://judgegpt.streamlit.app/).

## Project Overview

The project comprises a Streamlit application (`app.py`) that allows users to input details for generating news fragments using OpenAI's GPT models. It includes functionality for both manual data entry and automated news generation based on a set of predefined parameters loaded from `prompt_engine.json`. The generated content is intended for use in our sister project, [JudgeGPT](https://github.com/aloth/JudgeGPT), where participants are asked to assess whether they perceive the content as machine or human-generated.

## About the Name: RogueGPT

The name RogueGPT carries a significant meaning within the context of this project. The term "GPT" is used pars pro toto, a rhetorical device where the name of a part of something is used to refer to the whole. In our case, "GPT" refers not only to OpenAI's Generative Pre-trained Transformer models but also broadly encompasses a wider array of Large Language Models (LLMs). This naming choice signifies that while the project currently utilizes GPT models, it is not limited to them and is open to integrating other LLMs in the future. The prefix "Rogue" is deliberately chosen to highlight the contentious nature of using machine learning for the production of news content, which is often seen as a problematic issue. It serves as an allusion to ChatGPT, suggesting that RogueGPT takes a divergent, perhaps more controversial, path by engaging directly with the generation of (potentially fake) news fragments.

### Key Components

- `app.py`: The main Python script that runs the Streamlit application, handling user input, content generation, and database operations.

- `prompt_engine.json`: A configuration file that defines the structure for automated news generation, including templates, styles, and components for different languages.

- `requirements.txt`: Lists the Python package dependencies necessary for running the application.

## Installation

To run RogueGPT locally, follow these steps:

1. Clone this repository.
2. Install the required Python packages using pip:

    pip install -r requirements.txt

3. Run the Streamlit application:

    streamlit run app.py

## Usage

The application has two main tabs:
- **Manual Data Entry**: Allows users to manually input details for a news fragment, including content, source, and metadata.
- **Generator**: Utilizes the `prompt_engine.json` configuration to generate news fragments automatically based on selected criteria.

Generated fragments can be saved to a MongoDB database and are primarily meant to serve as input for the [JudgeGPT](https://github.com/aloth/JudgeGPT) project.

## Project Status

RogueGPT is in its early stages and is continuously evolving. The output generated by this project is experimental and intended for research purposes within the scope of understanding AI's impact on news authenticity.

## Contributing

We welcome contributions to RogueGPT! If you're interested in contributing, please fork the repository and submit your pull requests. We're excited to collaborate with the community to explore the capabilities and implications of generative AI in news creation.

## Future Directions and Unexplored Ideas for RogueGPT

RogueGPT, while already a significant step forward in the exploration of AI-generated content, has numerous avenues for expansion and enhancement. The project's potential growth areas are designed to elevate its capabilities, broaden its impact, and deepen its exploration into the interplay between AI and news creation:

- **Cross-Model Integration**: Beyond GPT, incorporating a wider array of generative models to diversify the types of content generated. This would allow RogueGPT to explore the nuances of different AI writing styles and effectiveness in mimicking human news writing across various domains.

- **Content Verification Layer**: Implementing a system that automatically checks the factual accuracy of generated content against trusted data sources. This layer would enhance the integrity of the generated news, and flag fake news automatically.

- **Trending Topics**: Tailoring the generation process to produce news content based on trending topics. This adaptation would make RogueGPT a more responsive tool, capable of catering to real-time global events.

- **Collaborative Editing Tools**: Developing features that enable multiple users to collaboratively edit and refine human-generated news fragments.

- **Integration with Fact-Checking Services**: Establishing partnerships with fact-checking organizations to vet the generated content for accuracy and bias. This would not only improve the credibility of the content but also provide valuable feedback for refining the AI models.

## License

RogueGPT is open-source and available under the GNU GPLv3 License. For more details, see the LICENSE file in the repository.

## Acknowledgments

This project leverages OpenAI's API for generating news fragments and pymongo for database interactions.

## Disclaimer

RogueGPT is an independent research project and is not affiliated with, endorsed by, or in any way officially connected to OpenAI. The use of "GPT" within our project name is purely for descriptive purposes, indicating the use of generative pre-trained transformer models as a core technology in our research. Our project's explorations and findings are our own and do not reflect the views or positions of OpenAI or its collaborators. We are committed to responsible AI research and adhere to ethical guidelines in all aspects of our work, including the generation and analysis of content.
