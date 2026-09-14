
#Improvements

the way we are searching in documents with images  and tables needs rework.
Let's try a more structured approach : 

1 -  We can take as assumption that :
  a - For most enterprise documents we will process in real life (the benchmarks is very wide...), the images will have a caption, or an alt_text is coming from Internet.  Moreover, using VLM to get image description is quite cheap these days. 

  b -  We will always use the Outline & Summarize Section option to analyze each  documents with a lightweight LLM. We can remove the case "no summarize" and thus simplify the code. 

  c - The Markownizer might change, and its capabilities to extract images, complex tables, ..  so we need flexibility there.
   The Mistral Markdownizer can extract images or not, and can either put tables as embedded Markdown or in separate HTML. Other Markdownizer always generate Markdown tables (or JSON, HTML,..  but we don't support them).

  d - If the table are in HTML, it's better to convert them in Markdown if no information is lost, so save token and possibly reduce LLM errors.  We could have  an helper function 'is_markdown_table" that looks for rowspan, colspan or table in cells.  I let you code it, with bs4 for example
  

2 - So an approach to investigate is : 

  - Modify how we deal with Mistral OCR produced an HTML table :  
     - If it can be converted to Markdown without loss, then convert it (you can use markdownify that we have as dependencies ) and remove the link produces by Mistral.
     - If it cannot be converted to Markdown without loss, then insert it has-is,  in html, in the Markdown (between <table> </table>tags) , remove the link, and add in comment the dimension of the table.

    - When processing the Markdown file with BAML summarizer LLM, send only the first lines of the table if it longer then 30 lines.
  
    - For images, keep the link in the Markdown, but instruct the summarizer LLM to check if the image is presented ou described in the text before (presentation of what is in the image ) and after the link (typically a caption). If it exists, thats enough.  If there's no clue, and if in the configuration there's an option that images larger than 10 kbites should be described, then call an LLM to get a description, and insert it in the Section Node. Provide the LLM the context (what is the document and section tite/description) and set un the prompt that if its a diagam it should extract and summarize content of legends, axes, ...

    - The summarizer  could also add in its answer a list of keywords to make search better. Same for the call to analyse images.

    - The table of content sent to the LLM (of displayed in the CLI command) should explitly mention description of the tables and images (if we have them) present in the section, except (if possible, to avoid repetitiion) if the section is almost only the table or the image.

    - So we can remove Nodes and Images nodes in the Graph. Remove Image Embeddings stuff. Update the tools. There should be no search_table, and no search_image

    - Instruct the agent (in Graph  navigation skill) that a) it should first use the table of content to get the answer and navigate in sections, b) avoid search c) grep is forbidden  d) Limit query image call, because  it is expensive (1 LLM call with the image). It should be called only when we have evidence that it analyzing the image can help in answering user request, with a precise query. This query should be written is a way the LLM says clearly it cannot answer.  
    There should not have more than 3 query images  per question (configurable).  Have a broader description to what can do query_image tool

   - Test with the mmlongbech benchmark project with a few documents and questions

   - Think, evaluated, seach weakness and pitsfall, ask questions, plan

    

    Cache this description in a file, so we won't have to call an LLM in case of re-run. Make a generic mechanism to cache BAML calls (key is )

    The skill sh



# Template
add     - genai_graph.core.commands_docgraph.DocGraphCommands

add check --extra 

The mmlongbench-doc bechmark is advancing. We have ns the dataset loaded.
Next step is to put the documents in the graph dtabase. But we need strong image understanding capabilities. 
Here what I have in mind to have good results: 
- I've recently added in the Mistral OCR based markdownizer the feature to extract images from the parsed PDF. They are stored in a separate directory with hash code as name, and the generated Markdown file is modified to insert this name as comment, in addition to the link to the image. 
- We can create Image nodes in the graph, with a relationship [CONTAINS] connecting MarkdownSection with them.
- These  Image nodes could have as field : 
   a -  the description of the image, if we succeed to extract it from a  possible caption  with a regexp (like "Fig. 1: ...", "Figure 2:... "  or using the Markdonw style - they are alway just after the link to the image, and often in italic, centered)
   b -  The embeddings if the image. Use (for now - configurable) the amazon/amazon.nova-2-multimodal-embeddings-v1 embeddings model provided by edenai
   c - size
   d - name (ie its hash code)
- The Agent could have new tools : 
  -  Image Search , to search an image in a document or a section by  its embeddings (and possibly its caption)
  -  Image query : It will call a VLM to answer a question regarding a provided model.  Use a configurable VLM  (start with GLM 5.3 Flash, as for the main agent - we might switch to a stronger model later )  

Update the build process to create such graph.  Do step by step. If you have  issue with image embeddings or other point, skip and report, we will investigate later. 
Test with the first file from the bechmark (or another one if it does not have image). Check that the graph looks correct and the new tools behave correctly/

Think, examine possible issues and alternatives, ask questions, prepare the plan.



