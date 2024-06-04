from __future__ import annotations

from typing import TYPE_CHECKING

from django.conf import settings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

if TYPE_CHECKING:
    from employees.models import DomainObjective, ObjectiveHistory


def ai_enhance_report(content: str) -> str:
    llm = ChatOpenAI(model=settings.OPENAI_MODEL, temperature=0, api_key=settings.OPENAI_KEY)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Please enhance the following text/report and make it more appealing with grammatically correct.",
            ),
            ("user", "{input}"),
        ]
    )

    chain = prompt | llm | StrOutputParser()

    return chain.invoke({"input": content})


def generate_ai_objective_progress_report(
    objective: DomainObjective, history: list[ObjectiveHistory]
) -> str:
    llm = ChatOpenAI(model=settings.OPENAI_MODEL, temperature=0, api_key=settings.OPENAI_KEY)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Please analyze the following objective history and generate a summary report for the objective. Ensure to show and evaluate the history overtime and give a consice summary. make sure to mention the status overall (e.g. good, bad, etc) of the history. mush answer in Dutch language, mush answer in Dutch language.",
            ),
            (
                "user",
                """### Objective ####
title: {title}
description: {description}

### objective history ###
<history>
{input}
</history>

### Report Summary & Analytsis ###
""",
            ),
        ]
    )

    formated_objective_history: str = "\n".join(
        [
            f"""
report id: {h.pk}
rating: {h.rating}
week: {h.week}
created at: {h.date}
content: \n{h.content}
\n
--------------------------------
"""
            for h in history
        ]
    )

    chain = prompt | llm | StrOutputParser()

    return chain.invoke(
        {
            "input": formated_objective_history,
            "title": objective.title,
            "description": objective.desc,
        }
    )
