"""Welcome to Reflex! This file outlines the steps to create a basic app."""

from rxconfig import config

import reflex as rx
import json
import time
import sys
import os
import asyncio

sys.path.append(os.getcwd())

import TreeHacksProject.searcher_dir.search_results as sr
import TreeHacksProject.searcher_dir.searcher as srcr
import TreeHacksProject.webSummarizer.summarizeWebPage as summarizer
import TreeHacksProject.prompt_engine.follow_up_question_generation as qg

class searchbarState(rx.State):
    """The state of the homepage searchbar"""
    oscillating: bool = True
    text: str = "Chest pain"
    word_list: list = json.load(open("assets/samples.json"))["terms"]
    word_index: int = 0
    def reset_states(self):
        self.oscillating = True
        self.text = "Chest pain"
        self.word_index = 0
        self.search_page = 0
    @rx.var
    def get_text(self) -> str:
        return self.text
    
    """The states of the search page"""
    _results: sr.SearchResults = None
    result_link1: str = ""
    result_title1: str = ""
    result_link2: str = ""
    result_title2: str = ""
    result_link3: str = ""
    result_title3: str = ""
    result_summary1: str = ""
    result_summary2: str = ""
    result_summary3: str = ""
    loading: bool = True
    loading_text: str = "Initializing search..."
    search_page: int = 0
    links_loading: bool = False

    """The states of the question pane"""
    prompt_question: str = ""
    _previous_questions: list[str] = []
    choices: list[str] = []
    num_choices: int = 0
    other_box: str = ""
    selected_answer: int = 0
    prompt_answer: str = ""



    #functions to enable word oscillations
    def pause_oscillation(self, text):
        self.oscillating = False
    def pause_oscillation_(self):
        self.oscillating = False
    def resume_oscillation(self, text):
        self.oscillating = True
    @rx.background
    async def iterate_word(self):
        while True:
            async with self:
                if self.oscillating:
                    self.text = self.word_list[self.word_index]
                    self.word_index = (self.word_index + 1) % len(self.word_list)
                    time.sleep(0.1)
    
    #functions to run a search
    async def get_results(self):
        self.loading = True
        self.links_loading = False
        yield # allow for other thread to launch loading screen
        self.loading_text = "Searching the web..."
        self._results = srcr.search(self.text)
        num_results = len(self._results.results)
        self.result_title1 = self._results.results[(self.search_page * 3 + 0) % num_results][0] # 10 results, 3 per page
        self.result_link1 = self._results.results[(self.search_page * 3 + 0) % num_results][1]
        self.result_title2 = self._results.results[(self.search_page * 3 + 1) % num_results][0]
        self.result_link2 = self._results.results[(self.search_page * 3 + 1) % num_results][1]
        self.result_title3 = self._results.results[(self.search_page * 3 + 2) % num_results][0]
        self.result_link3 = self._results.results[(self.search_page * 3 + 2) % num_results][1]
        self.loading_text = "Summarizing results..."
        self.result_summary1 = summarizer.get_summary(self.result_link1)
        self.result_summary2 = summarizer.get_summary(self.result_link2)
        self.result_summary3 = summarizer.get_summary(self.result_link3)

        # generate questions
        self.loading_text = "Generating prompts..."
        self.prompt_question = qg.generate_follow_up_question(self.text, self._previous_questions)
        self.choices, self.prompt_question = qg.get_multiple_choice(self.prompt_question)
        self._previous_questions.append(self.prompt_question)
        self.num_choices = len(self.choices)
        self.loading = False

    #function to go to next page of results
    def next_page(self):
        self.links_loading = True
        yield
        self.search_page += 1
        num_results = len(self._results.results)
        self.result_title1 = self._results.results[(self.search_page * 3 + 0) % num_results][0] # 10 results, 3 per page
        self.result_link1 = self._results.results[(self.search_page * 3 + 0) % num_results][1]
        self.result_title2 = self._results.results[(self.search_page * 3 + 1) % num_results][0]
        self.result_link2 = self._results.results[(self.search_page * 3 + 1) % num_results][1]
        self.result_title3 = self._results.results[(self.search_page * 3 + 2) % num_results][0]
        self.result_link3 = self._results.results[(self.search_page * 3 + 2) % num_results][1]
        self.loading_text = "Summarizing results..."
        self.result_summary1 = summarizer.get_summary(self.result_link1)
        self.result_summary2 = summarizer.get_summary(self.result_link2)
        self.result_summary3 = summarizer.get_summary(self.result_link3)
        self.links_loading = False

    #function to answer a prompt
    def answer_prompt_mc(self, choice: int):
        self.prompt_answer = self.choices[choice]
        self.text = qg.refine_query(self.text, self.prompt_answer, self.prompt_question)
        self.loading = True
        self.search_page = 0
        return searchbarState.get_results()

    def answer_prompt_open(self):
        self.prompt_answer = self.other_box
        self.text = qg.refine_query(self.text, self.prompt_answer, self.prompt_question)
        self.loading = True
        self.search_page = 0
        return searchbarState.get_results()
    
    def reset_values(self):
        self._results = None
        self.result_link1 = ""
        self.result_title1 = ""
        self.result_link2 = ""
        self.result_title2 = ""
        self.result_link3 = ""
        self.result_title3 = ""
        self.result_summary1 = ""
        self.result_summary2 = ""
        self.result_summary3 = ""
        self.loading = True
        self.loading_text = "Initializing search..."
        self.prompt_question = ""
        self._previous_questions = []
        self.choices = []
        self.num_choices = 0
        self.other_box = ""
        self.selected_answer = 0
        self.prompt_answer = ""
        self.search_page = 0
        self.links_loading = False

    


    
    # def update_result_fields(self, index: int):
    #     self.result_title = self._results.results[0][0]
    #     self.result_link = self._results.results[0][1]


    



# class QueryState(rx.State):
#     text: str = "pig"
#     def init_query(self):
#         self.text = searchbarState.text
#         print(self.text)



@rx.page(on_load=searchbarState.reset_states)
def index() -> rx.Component:
    return rx.center(
        rx.flex(
            rx.image(src="/rondo.png", width="20em"),
            rx.vstack(
                rx.heading("Welcome to Rondo!", size="9"),
                rx.hstack(
                    rx.input(size="4",
                            value = searchbarState.text,
                            on_focus=searchbarState.pause_oscillation,
                            on_mount=searchbarState.iterate_word,
                            on_change=searchbarState.set_text,),
                    rx.link(
                        rx.button(
                        "Go",
                        size="4",
                        on_click=searchbarState.pause_oscillation_),
                        href="/search"
                    )
                ),
                align="center",
                font_size="2em",
                spacing = "4",
            ),
            direction="column",
            align="center"
        ),
        height="75vh",
    )

@rx.page(on_load=searchbarState.get_results)
def search() -> rx.Component:
    return rx.box( 
        rx.flex(
            rx.link(
                rx.card("New Search",
                        color="white",
                        background_color="blue",
                        _hover={
                            "color": "blue",
                            "background_color": "white",
                            "cursor": "pointer"
                        },
                        size="2",
                        on_click=searchbarState.reset_states),
                href="/"
            ),
            rx.spacer(),
            rx.image(src="/rondo.png", width="8em", align="center"),
            # rx.center(
            #     rx.vstack(
            #         rx.heading("Search Results:", size="7"),
            #         padding="10px"
            #     )
            # ),
            rx.spacer(),
            rx.spacer(),
            padding="10px"
        ),
        rx.box(
            rx.hstack(
                rx.text("Query: ",size = "8", weight = "bold"),
                rx.text(searchbarState.text, size="8", weight="medium"),
            ),
            width="100%",
            background_color="var(--accent-2)",
            border_radius="15px",
            align = "start",
            padding = "5px"
        ),
        # show loading screen if results are not ready yet
        rx.cond(
            searchbarState.loading,
            rx.center(
                rx.vstack(
                    rx.chakra.circular_progress(is_indeterminate=True),
                    rx.text(searchbarState.loading_text,color="navy"),
                    align="center"
                ),
                height="75vh"
            ),
            rx.grid(
                rx.card(rx.heading("Improve your search:", size="7"),
                        rx.box(
                            rx.heading(
                                searchbarState.prompt_question,
                                color = "navy"
                            ),
                            rx.flex(
                                rx.foreach(
                                    rx.Var.range(searchbarState.num_choices - 1),
                                    lambda i: rx.card(searchbarState.choices[i],
                                                    on_click=searchbarState.answer_prompt_mc(i),
                                                    _hover={
                                                        "color": "white",
                                                        "background_color": "navy",
                                                        "cursor": "pointer"})
                                ),
                                rx.card(
                                    rx.hstack(
                                        rx.text("Other:"),
                                        rx.input(on_change=searchbarState.set_other_box),
                                        rx.button(
                                            "Go",
                                            size="2",
                                            on_click=searchbarState.answer_prompt_open
                                        )
                                    )
                                ),
                                spacing = "4",
                                direction="column",
                            )
                        ),
                        width="100%",
                        background_color="var(--plum-2)",
                        border_radius="15px",
                        padding = "5px",
                ),
                rx.card(
                    rx.flex(
                            rx.heading("Results", size="7"),
                            rx.spacer(),
                            rx.button("Refresh", size="2", on_click=searchbarState.next_page),
                            padding="10px"
                    ),
                    rx.cond(
                        searchbarState.links_loading,
                        rx.center(
                            rx.vstack(
                                rx.chakra.circular_progress(is_indeterminate=True),
                                rx.text("Refreshing links...",color="navy"),
                                align="center"
                            ),
                            height="75vh"
                        ),
                        rx.box(
                            rx.flex(
                                rx.link(
                                    rx.card(
                                        rx.heading(searchbarState.result_title1),
                                        rx.text(searchbarState.result_summary1),
                                        on_click = rx.redirect(
                                            searchbarState.result_link1,
                                            external=True
                                        ),
                                        _hover={
                                            "color": "white",
                                            "background_color": "navy",
                                            "cursor": "pointer"}
                                    ),
                                ),
                                rx.divider(),
                                rx.link(
                                    rx.card(
                                        rx.heading(searchbarState.result_title2),
                                        rx.text(searchbarState.result_summary2),
                                        on_click = rx.redirect(
                                        searchbarState.result_link2,
                                        external=True
                                        ),
                                        _hover={
                                            "color": "white",
                                            "background_color": "navy",
                                            "cursor": "pointer"}
                                    ),
                                ),
                                rx.divider(),
                                rx.link(
                                    rx.card(
                                        rx.heading(searchbarState.result_title3),
                                        rx.text(searchbarState.result_summary3),
                                        on_click = rx.redirect(
                                            searchbarState.result_link3,
                                            external=True
                                        ),
                                        _hover={
                                            "color": "white",
                                            "background_color": "navy",
                                            "cursor": "pointer"}
                                    ),
                                ),
                                spacing = "4",
                                direction="column",
                            ),
                            width="100%",
                            background_color="var(--plum-2)",
                            border_radius="15px",
                            padding = "5px",
                        )
                    )
                    
                ),
                columns = "2"
            )
        )
    )


app = rx.App()
app.add_page(index)
app.add_page(search)
