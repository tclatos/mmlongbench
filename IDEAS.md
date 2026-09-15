
#Improvements



    

    Cache this description in a file, so we won't have to call an LLM in case of re-run. Make a generic mechanism to cache BAML calls (key is )

    The skill sh



# Template
add     - genai_graph.core.commands_docgraph.DocGraphCommands

add check --extra 

Check aligbed skills/development/benchmark-framework/SKILL.md: 
mmlongbench/skills/custom/mmlongbench-qa/SKILL.md




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



