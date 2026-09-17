#Improvements
Don't loop after : 
LLM call failed for NETFLIX_2015_10K_pdf.md branch [PART I]: Error code: 403 - {'error': {'message': 'Key limit exceeded (monthly limit). Manage it using https://openrouter.ai/workspaces/default/keys/f1478d7f50b9f060e764ae38ea8e4ae91d7bfffd3898e6a8ab339bd12c25efaf', 'code': 403}}


Seen :
09:54:59.852 | INFO    | Task run 'outline-ddoseattle-150627210357-lva1-app6891_95' - Finished in state Completed()
[2026-09-17T07:55:10Z ERROR jsonish::jsonish::parser::multi_json_parser] Failed to parse JSON object: Failed to parse JSON

Seen : 
10:27:46-WARNING | merge.py:972 merge_relationships_batch- Batch LOAD FROM failed for HAS_SUBSECTION (13082 rows): Buffer manager exception: Unable to allocate memory! The buffer pool is full and no memory could be freed!; falling back to point merges

10:27:46-WARNING | merge.py:972 merge_relationships_batch- Batch LOAD FROM failed for HAS_SUBSECTION (13082 rows): Buffer manager exception: Unable to allocate memory! The buffer pool is full and no memory could be freed!; falling back to point merges
10:29:55-WARNING | stopwords.py:271 get_stopwords- Could not load spaCy stop words for 'en': No module named 'spacy'
10:29:55-INFO    | ingest.py:377 ingest_document_graph- Document Graph ingest: 135 processed (1 skipped), 0 failed, 13216 section(s), 0 chunk(s), 13350 rel(s)
10:29:58-SUCCESS | build.py:284 build_document_graph- Document Graph build complete: {'documents_processed': 135, 'documents_failed': 0, 'documents_skipped': 1, 'sections_created': 13216, 'sections_summarized': 2507, 'chunks_created': 0, 'relationships_created': 13350, 'embeddings_model': None, 'embeddings_dim': None, 'fts_index': 'section_fts', 'warnings': [], 'db_path': '/home/tcl/prj/mmlongbench/data/kg/mmlongbench_multi.db', 'files_degraded': 0, 'timings': {'ingest_s': 288.694}}


# Perf
 Parallelize document_graph_factory.py:232 extract_outlines
    

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



