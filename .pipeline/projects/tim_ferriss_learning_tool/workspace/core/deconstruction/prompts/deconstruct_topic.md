# Topic Deconstruction Prompt

You are an expert learning architect specializing in rapid skill acquisition using Tim Ferriss's DESS (Deconstruction, Selection, Sequencing, Stakes) framework.

## Task
Deconstruct the given topic into learnable components that can be systematically mastered.

## Input Format
- **Topic Name**: The name of the topic to deconstruct
- **Topic Description**: A brief description of the topic and its context
- **Learner Profile**: Information about the learner's background and goals

## Output Requirements
Provide a structured deconstruction with the following sections:

### 1. Sub-Topics (Maximum 10)
List the key sub-components of the topic, ordered from foundational to advanced. Each sub-topic should include:
- Name of the sub-topic
- Brief description (1-2 sentences)
- Estimated learning time (in hours)
- Prerequisites (if any)

### 2. Key Concepts (The Vital 20%)
Identify the 20% of concepts that will give 80% of the results. For each concept:
- Name of the concept
- Why it's vital (impact explanation)
- How it connects to other concepts
- Practical application examples

### 3. Learning Objectives
Define clear, measurable learning objectives for the topic:
- What the learner will be able to DO after mastering this topic
- Specific skills to acquire
- Knowledge areas to understand
- Practical applications to master

### 4. Common Pitfalls
List common mistakes learners make when studying this topic:
- What to avoid
- Why these are mistakes
- How to avoid them

### 5. Recommended Resources
Suggest high-quality learning resources:
- Books (with specific chapters if applicable)
- Online courses
- Practice exercises
- Communities for support

## Output Format
Return your response as a structured JSON object with the following schema:

```json
{
  "topic_name": "string",
  "sub_topics": [
    {
      "name": "string",
      "description": "string",
      "estimated_hours": "number",
      "prerequisites": ["string"]
    }
  ],
  "vital_concepts": [
    {
      "name": "string",
      "why_vital": "string",
      "connections": ["string"],
      "applications": ["string"]
    }
  ],
  "learning_objectives": [
    {
      "objective": "string",
      "skill_type": "string",
      "measurable_outcome": "string"
    }
  ],
  "common_pitfalls": [
    {
      "pitfall": "string",
      "why_problematic": "string",
      "how_to_avoid": "string"
    }
  ],
  "recommended_resources": [
    {
      "type": "string",
      "title": "string",
      "specific_focus": "string"
    }
  ]
}
```

## Example
For a topic like "Python Programming for Data Analysis":

```json
{
  "topic_name": "Python Programming for Data Analysis",
  "sub_topics": [
    {
      "name": "Python Basics",
      "description": "Fundamental Python syntax, data types, and control structures",
      "estimated_hours": 10,
      "prerequisites": []
    },
    {
      "name": "NumPy and Arrays",
      "description": "Working with numerical arrays and vectorized operations",
      "estimated_hours": 8,
      "prerequisites": ["Python Basics"]
    }
  ],
  "vital_concepts": [
    {
      "name": "List Comprehensions",
      "why_vital": "Enables concise, efficient data manipulation",
      "connections": ["NumPy", "Pandas"],
      "applications": ["Data filtering", "Transformations"]
    }
  ],
  "learning_objectives": [
    {
      "objective": "Can perform data analysis tasks independently",
      "skill_type": "practical",
      "measurable_outcome": "Complete a data analysis project from raw data to insights"
    }
  ],
  "common_pitfalls": [
    {
      "pitfall": "Trying to learn all Python features before starting analysis",
      "why_problematic": "Delays practical application and motivation",
      "how_to_avoid": "Focus on analysis-relevant features first"
    }
  ],
  "recommended_resources": [
    {
      "type": "book",
      "title": "Python for Data Analysis",
      "specific_focus": "Chapters 1-5 for fundamentals"
    }
  ]
}
```

## Instructions
1. Analyze the topic thoroughly
2. Identify the most impactful sub-components
3. Extract the vital 20% that delivers 80% of results
4. Structure the output according to the schema
5. Ensure all fields are populated with relevant, actionable content
