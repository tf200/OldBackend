from django.conf import settings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI


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
