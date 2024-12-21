Autoprompt
==========

Overview
--------
Autoprompt is an intent-based prompt calibration algorithm that is utilized to dynamically generate tools to cater to various user needs. The tools are essentially designed to generate python code to solve the task.

Functions
---------

.. py:function:: identify_challenging_examples(task_description, input_prompt)

    Generate challenging examples for the given task description.

    :param str task_description: The task for which examples are to be generated.
    :param str input_prompt: The prompt used to generate the challenging examples.
    :return: List of challenging examples.
    :rtype: list

.. py:function:: annotate_challenging_examples(examples, input_prompt)

    Annotate challenging examples with corresponding Python code generated from the LLM.

    :param list examples: List of challenging examples.
    :param str input_prompt: The prompt to generate code for the examples.
    :return: List of dictionaries containing the example and its corresponding code.
    :rtype: list of dict

.. py:function:: annotate(annotations, initial_prompt)

    Analyze and rank errors in the generated code for each example.

    :param list annotations: List of dictionaries with challenging examples and their generated code.
    :param str initial_prompt: The initial prompt used for code generation.
    :return: List of examples with detailed error analysis and scores.
    :rtype: list of dict

.. py:function:: error_analysis_fun(input_prompt, annots)

    Perform error analysis for the provided annotations and input prompt.

    :param str input_prompt: The prompt used for generating code for challenging examples.
    :param list annots: List of annotated examples with errors.
    :return: Detailed analysis of errors.
    :rtype: str

.. py:function:: calibrate_generation_prompt(input_prompt, history, error_analysis, task_desc, meta_prompt)

    Refine the input prompt based on task details, history, and error analysis.

    :param str input_prompt: The prompt to be refined.
    :param list history: A list of previously generated prompts.
    :param list error_analysis: A list of identified errors.
    :param str task_desc: A description of the task.
    :param str meta_prompt: A base prompt used for code generation.
    :return: Refined prompt.
    :rtype: str

.. py:function:: autoprompt(task_description, num_iter)

    Iteratively refine the base meta prompt for the given task description.

    :param str task_description: A description of the task to refine the prompt for.
    :param int num_iter: The number of iterations to refine the prompt.
    :return: The final refined prompt.
    :rtype: str

Recommended Usage:

   .. code-block:: python

      refined_prompt = autoprompt("Generate Python code for data cleaning tasks", 5)

Error Handling
--------------
The Autoprompt system includes robust error handling for:

* Module installation errors during code execution.
* Tool calling errors for generating incorrect responses.
* Challenging example analysis failures.

Requirements
------------
* sys
* re
* subprocess
* traceback