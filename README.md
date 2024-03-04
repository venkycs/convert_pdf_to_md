# PDF to Markdown Conversion Tool

## Description
This tool is designed to efficiently convert PDF documents into Markdown format, making it especially useful for generating training material for Large Language Models (LLMs). It features advanced text and font extraction, font ranking for accurate heading detection, and efficient processing on CPU architectures.

## Features
- **LLM-Focused Extraction**: Optimized for LLM training material with attention to complex language structures and technical terminologies.
- **Efficient CPU Performance**: High efficiency on various CPU systems, ensuring wide accessibility and practicality.
- **Font Ranking System**: Sophisticated system for font size-based ranking, crucial for accurate Markdown heading levels.
- **Batch Processing**: Ability to process multiple PDF files simultaneously for increased efficiency.
- **Advanced Logging**: Comprehensive logging system for effective monitoring and troubleshooting.
- **MD5 Hash Management**: Efficient handling of document processing to avoid redundancy.
- **JSON Data Handling**: Capability to write detailed text and font information into JSON files.

## Installation
Installation is easy and got minimal dependencies, it works very well with CPU and can scale.
### Clone the Repository
Start by cloning the repository to your local machine:

```bash
git clone https://github.com/venkycs/convert_pdf_to_md.git
cd convert_pdf_to_md
python -m venv .
source bin/activate
python convert_pdf_to_md.py
```

## Contributing

Contributions are welcome. Please follow these steps to contribute:
1. Fork the repository.
2. Create a new branch: `git checkout -b <your-branch-name>`.
3. Make your changes and commit them: `git commit -am 'Add some feature'`.
4. Push to the original branch: `git push origin <your-branch-name>`.
5. Create the pull request.

## License
This project is licensed under the [MIT License](LICENSE).

## Acknowledgments
- PyMuPDF for PDF processing capabilities.
- Contributors who participate in the development of this tool.

## Version History
- 1.0
    - Initial Release
