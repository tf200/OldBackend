from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from django.conf import settings
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
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


def ai_summarize(content: str, default="no content") -> str:
    llm = ChatOpenAI(model=settings.OPENAI_MODEL, temperature=0, api_key=settings.OPENAI_KEY)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Please summarize the following text/report, make sure to give a concise summary that includes all the importent information."
                + (
                    f"If you find nothing to summarize, return '{default}' and nothing else."
                    if default
                    else ""
                ),
            ),
            ("user", "{input}"),
        ]
    )

    chain = prompt | llm | StrOutputParser()

    return chain.invoke({"input": content})


def ai_smart_formula(
    domain: str,
    goal: str,
    format: Literal["TEXT", "JSON"] = "TEXT",
    objective_number=3,
    language: str = "English",
    start_date: None | str = None,
    end_date: None | str = None,
) -> str | dict[str, Any]:
    llm = ChatOpenAI(model=settings.OPENAI_MODEL, temperature=0, api_key=settings.OPENAI_KEY)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                'Please create an accurate {objective_number} objectives for the following goal to achieve it using SMART Formula, the goal(s) in "{domain}" field ({period_dates}), ensure to destribute the time/period over objectives if needed, {language_string}:',
            ),
            ("user", "Goal: {goal}\n{format_string}"),
        ]
    )

    json_format = """{
        "objectives": [
            {
                "specific": "",
                "measurable": "",
                "achievable": "",
                "relevant": "",
                "time_bound": ""
            },
            ...(repeat for {objective_number} objectives)
        ]
    }"""

    format_string: str = "Ensure to return only in {format} format."

    language: str = language if language is not None else "English"
    language_string: str = "Answer in {language} language."

    period_dates: str = ""
    if start_date and end_date:
        period_dates = f"Period: from {start_date} to {end_date}"

    if format == "TEXT":
        chain = prompt | llm | StrOutputParser()
    elif format == "JSON":
        chain = prompt | llm | JsonOutputParser()
        format_string = format_string.format(format="JSON") + ":\n" + json_format

    return chain.invoke(
        {
            "domain": domain,
            "goal": goal,
            "format": format,
            "objective_number": objective_number,
            "format_string": format_string,
            "language_string": language,
            "start_date": start_date,
            "end_date": end_date,
            "period_dates": period_dates,
        }
    )
