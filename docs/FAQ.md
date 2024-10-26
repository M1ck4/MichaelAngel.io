# Frequently Asked Questions (FAQ)

### What are the system requirements for running the MichaelAngel.io tools?

To run the MichaelAngel.io tools efficiently, you should have:

-    Python 3.7 or higher installed.
-    Sufficient CPU/GPU power for handling image processing and AI training.
-    Libraries such as Pillow, OpenCV, SQLAlchemy, and Requests.
-    Consider using a virtual environment to manage dependencies.
-    Each tools requirements.txt file

### What is MichaelAngel.io?

MichaelAngel.io is a project by M1ck4 that focuses on building an ethical AI framework using Creative Commons licensed content. The goal is to create a toolset for artists, game developers, and other creators that respects copyright and fosters sustainable and responsible use of media.

### What is the target audience for MichaelAngel.io framework?

The MichaelAngel.io Framework is designed for a diverse audience, including professional artists, game developers, traditional artists, AI researchers, data scientists, and educators. 
It offers tools that cater to sculptors, texture artists, character creators, and those involved in AI development, data analysis, and ethical dataset creation.

### What is Curator?

Curator is a downloader program that accesses Creative Commons image sites like Pixabay, Unsplash, Pexels, and Flickr. It is designed to efficiently search, download, and organize images based on specified search terms while respecting copyright guidelines.

### Can I add new APIs to Curator for sourcing images?

Yes, Curator is designed to be extendable:

-    You can add new API sources by modifying the config.yaml file or extending Curator’s code.
-    Ensure that any additional sources follow Creative Commons guidelines to maintain ethical standards.

### How does Chisel work?

Chisel is the preprocessing tool for MichaelAngel.io. It handles tasks such as resizing images, checking dimensions, detecting blurriness, and ensuring that downloaded content meets quality standards for training AI. Chisel prepares images so they’re suitable for creating high-quality datasets.

### What does Muse do?

Muse is a dataset creator and manager. It organizes preprocessed images into structured datasets, splits data for training and validation, performs data augmentation, and handles format conversions. Muse also integrates with TagTuner to automate tagging and metadata generation, ensuring datasets are optimized for training MichaelAngel.io.

### How does FilmFrame fit into the pipeline?

FilmFrame extracts still frames from Creative Commons-licensed movies to create training sets. It automates metadata tagging to ensure proper attribution and is ideal for generating large quantities of training data from video sources while adhering to ethical standards.

### How are the tools interconnected in the MichaelAngel.io pipeline?

The tools in the MichaelAngel.io pipeline are designed to work together while maintaining independence:

-    Curator downloads images.
-    Chisel preprocesses and cleans images.
-    Muse organizes images into datasets.
-    FilmFrame extracts and preprocesses movie stills.

### What if I only want to use one tool from the pipeline?

Each tool in the MichaelAngel.io suite can be used independently. If you only need to download images, you can use Curator alone. Similarly, eith the other tools. The modular design allows flexibility based on your project's needs.

### How does Muse handle dataset splitting and augmentation?

Muse can automatically split datasets into training, validation, and test sets. It also supports data augmentation techniques like flipping, rotation, cropping, and scaling to enrich the dataset and improve AI training. These options can be configured to suit specific requirements.

### How does Scribe ensure proper Creative Commons attribution?

Scribe aggregates metadata information from every stage of the pipeline, pulling attribution details from each tool (like Curator and FilmFrame). This creates a centralized and transparent record, ensuring that proper credit is given to all Creative Commons sources used in the dataset.

### What if I encounter an error while using one of the tools?

If you encounter an error:

-    Use the GitHub Issues page to report any bugs or problems.
-    Follow error-handling guidelines in the relevant tool's documentation.
-    Consider contributing to the project by suggesting fixes or submitting a pull request.

### Can I customize the configuration for each tool?

Yes, each tool in the MichaelAngel.io framework is configurable:

-    Use config.yaml files to adjust search terms, image sizes, and processing parameters.
-    Modify threading settings and error handling in Curator to optimize download efficiency.
-    Set data augmentation parameters in Muse for custom dataset configurations.

### How does the project ensure data ethics and sustainability?

MichaelAngel.io is built with a focus on data ethics and sustainability:

 -   Curator strictly adheres to Creative Commons licensing when sourcing images.
 -   Chisel ensures that only high-quality and relevant images are used.
 -   Scribe provides transparent attribution, ensuring that all Creative Commons sources are clearly documented.
 -   The entire pipeline is designed to respect copyright laws and support sustainable AI development.

### What programming languages are used in the tools?

The primary programming language for MichaelAngel.io tools is Python. Libraries like Pillow, OpenCV, SQLAlchemy, and others are utilized for image processing, database management, and efficient data handling throughout the pipeline.

### How can I contribute to the development of MichaelAngel.io?

To contribute:

-    Read the Contributing_Guide.md in the docs folder.
-    Fork or clone the repository and make your modifications.
-    Submit a pull request with detailed information about your changes.
-    Follow the code style guidelines and ensure proper attribution if you use any Creative Commons content.


### What is the purpose of this modified project?

This modified project builds upon the original work of MichaelAngel.io, incorporating new features, improvements, or adaptations based on the needs of the user or contributor. Modifications are encouraged as long as they respect the original license terms.

### What does the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 (CC BY-NC-SA 4.0) License mean?

This license allows you to:

-  Share: Copy and redistribute the material in any medium or format.
-  Adapt: Remix, transform, and build upon the material. However, you must follow these conditions:
-  Attribution: You must give appropriate credit to the original creator.
-  NonCommercial: You cannot use the material for commercial purposes.
-  ShareAlike: If you make modifications, you must distribute your contributions under the same license as the original.
-   Additional Restrictions: You cannot impose legal terms or technological measures that legally restrict others from exercising the rights granted by the license.

### How do I properly attribute the original work in my modified version?

To attribute the original work in your modified version, follow this template:

-  Clearly mention the original project title and the creator (e.g., "Based on MichaelAngel.io by M1ck4").
-  Include a link to the original project material.
-  Describe any changes you made to the original.
-  Ensure your modifications are licensed under the same CC BY-NC-SA 4.0 license.

### Can I use the material from this project commercially?

No, the NonCommercial clause of the license prohibits the use of this material for commercial purposes. You may use it for personal projects, educational purposes, or other non-commercial uses, but not for any activity that seeks commercial advantage or monetary compensation.

### What if I modify the project and want to share my version?

If you modify the project:

-  Clearly attribute the original work to M1ck4 and indicate what changes you've made.
-  Use the same CC BY-NC-SA 4.0 license for your modified version.
-  Provide a link to the original work and mention that your version is a derivative.

### What constitutes appropriate credit under this license?

Appropriate credit includes:

-  The name of the original creator (M1ck4) and the original project title (MichaelAngel.io).
-  A link to the original material.
-  An indication of what changes you made.
-  A statement that the original work is licensed under the CC BY-NC-SA 4.0 license.

### How do I handle attribution if I’m using content from MichaelAngel.io?

You should create an ATTRIBUTION.md file in your modified project that includes:

-  The original creator’s name.
-  A description of your changes.
-  A link to the original project material.
-  Confirmation that your modified version follows the same license conditions.

### What if I don't want to share my modifications?

If you make modifications to the project, the ShareAlike condition requires that you share your modified version under the same license (CC BY-NC-SA 4.0). This promotes openness and collaboration within the community.

10. Can I modify the attribution format?

Yes, you can modify the format of the attribution for clarity or presentation purposes, as long as all the necessary elements are included: the original creator's name, a description of changes, a link to the original work, and a statement about the license.

### How can I make sure my contributions are compliant?

To ensure compliance:

-  Use the ATTRIBUTION.md template provided.
-  Stick to the CC BY-NC-SA 4.0 license requirements.
-  Follow the instructions in the Attribution Guide for proper credit.

### How do I contact M1ck4 for more information?

If you have specific questions about the project or need further guidance on attribution, you can reach out via:

-  GitHub Issues: https://github.com/M1ck4/MichaelAngel.io/issues
-  Email: michaelangelo_io@protonmail.com

### What if I find a mistake in the original project?

If you find an error or issue in the original project, you can:

-  Submit a bug report or feature request through the GitHub Issues page.
-  Fork the repository, make corrections, and submit a pull request with your modifications.
-  Ensure your modifications comply with the original license terms.

### What happens if I receive a request to remove attribution?

If you receive a request to remove attribution from the original creator, you must comply to the extent reasonably practicable. This means:

-  Removing the creator’s name if requested.
-  Informing the creator that the request has been handled.

### Can I use Creative Commons content in my contributions to MichaelAngel.io?

Yes, as long as the content you contribute follows the CC BY-NC-SA 4.0 or a compatible license. Be sure to provide proper attribution for any Creative Commons content you include and ensure it aligns with the project's non-commercial requirements.

### Can I contribute my own data or media to MichaelAngel.io?

Yes, you can contribute data or media, but make sure that any contributions are compliant with the project's guidelines. Any content you contribute must either:

-  Be your original work.
-  Be properly attributed and licensed under a compatible Creative Commons license, like CC BY or CC BY-SA.
-  Follow non-commercial and share-alike requirements to maintain project consistency.

### What if I want to use a different license for my modifications?

All modifications of MichaelAngel.io must remain under the CC BY-NC-SA 4.0 license. You cannot change the license to a different one because the share-alike requirement ensures that all derivative works stay under the same license terms.

### Is there a limit to how much I can modify in my version?

There are no restrictions on how much you can modify, adapt, or build upon MichaelAngel.io, as long as:

-  You provide proper attribution to the original creator.
-  You do not use the material for commercial purposes.
-  You continue to license your modifications under the CC BY-NC-SA 4.0 license.

### Do I have to make my modifications publicly available?

No, you are not required to make your modifications public. However, if you distribute or share your modified version with others, you must follow the attribution and licensing requirements outlined by CC BY-NC-SA 4.0.

### Can I create private forks or versions of MichaelAngel.io for internal use?

Yes, you can create private versions or forks for internal, non-commercial use without making them public. Just remember that if you decide to share these versions outside your organization or network, you need to comply with the attribution and license requirements.

### What if I integrate MichaelAngel.io with other open-source projects?

Integration with other open-source projects is allowed as long as the other projects' licenses are compatible with CC BY-NC-SA 4.0. Ensure that:

-  The integration respects the non-commercial clause.
-  The final integrated project maintains a share-alike license.
-  Proper attribution is given for both MichaelAngel.io and the other integrated projects.

### How do I handle third-party libraries or resources used in MichaelAngel.io?

If you incorporate third-party libraries, APIs, or other resources:

-  Make sure they are compatible with the CC BY-NC-SA 4.0 license.
-  Provide proper attribution to those third-party resources, especially if they require acknowledgment.
-  Include references to their respective licenses in your modified project's ATTRIBUTION.md.

### Do I need to attribute specific APIs or tools used in MichaelAngel.io if I modify the project?

Yes, if you continue to use specific APIs, tools, or services (like Google APIs, Pixabay, Unsplash, etc.) in your modifications, you should:

-  Acknowledge those resources in your ATTRIBUTION.md.
-  Provide links to their respective documentation or terms of service.
-  Ensure you comply with the licensing and usage guidelines specific to those resources.
