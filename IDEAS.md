To run the mmlongbench, we need strong image understanding capabilities. 
Here what I have in mind to have good results: 
- I've recently added in the Mistral OCR based markdownizer the feature to extract images from the parsed PDF. They are stored in a separate directory with hash code as name, and the generated Markdown file is modified to insert this name as comment, in addition to the link to the image. 

amazon/amazon.nova-2-multimodal-embeddings-v1:0

