import openai
import string
import os

# Set up your OpenAI API key
openai.api_key = str(os.environ['OPENAI_API_KEY'])

def generate_follow_up_question(input_query, previous_questions):
    # Constructing the prompt for ChatGPT

    prompt = f"Pretend I am a person who does not have robust technology literacy and does not know how to make specific and well defined search queries. I look up {input_query}. What is the most important follow up question you might need to ask me in order to get a more specific and well defined search query? For the follow up question, I want it to be very simple, specific, easy to answer with a 2-4 categorical answers that are provided in square brackets [(a) choice 1 * (b) choice 2 * (c) choice 3 * ...)] where each choice is delimited by a * symbol and there is ALWAYS an option that says 'Other' as the last option, but the other option also needs to have a letter in front of it and should be structured the same way as all the other options. The answers provided MUST follow this exact format and they MUST be surrounded by square brackets. I do not want it to be a compound question. I want it to be just ONE simple question not multiple. Make sure that the question is NOT repetitive. Do not ask about information already included in the input. Make sure all questions and multiple choice answers are formatted the same way. Do not ask questions that are similar to any of the previous questions. DO NOT have 'Please specify' in any of your multiple choice answers and do not use parentheses of any kind in the actual question."
    questions_str = ", ".join(previous_questions)
    prompt = prompt + "previous questions:" + questions_str
    # Generate response from ChatGPT
    response = openai.chat.completions.create( 
        model = "gpt-4",
        messages = [{
            "role" : "user",
            "content" : prompt
        }],
        #prompt = prompt,
        max_tokens=256,
        temperature=1,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    # Extracting the follow-up questions from the response
    print(response.choices[0].message.content)
    follow_up_question = response.choices[0].message.content

    return follow_up_question

def prompt_user(question):
    # Prompting the user to answer the follow-up question
    user_answer = input(f"{question} ")
    return user_answer

def remove_common_words(s1, s2):
    # Split the strings into words
    words1 = s1.split()
    words2 = s2.split()

    translation_table = str.maketrans('', '', string.punctuation)
    
    # Process each word
    processed_words1 = []
    for word in words1:
        # Convert to lowercase
        word = word.lower()
        # Remove punctuation
        word = word.translate(translation_table)
        # Append processed word
        processed_words1.append(word)

    processed_words2 = []
    for word in words2:
        # Convert to lowercase
        word = word.lower()
        # Remove punctuation
        word = word.translate(translation_table)
        # Append processed word
        processed_words2.append(word)

    # Convert lists of words into sets for efficient membership testing
    set2 = set(processed_words2)

    # Remove words from s1 that are in s2
    result_words = [word for word in processed_words1 if word not in set2]

    # Join the remaining words back into a string
    result = ' '.join(result_words)

    return result


def refine_query(user_input, user_answer, follow_up_question):
    # Generate a more specific version of the original query
    prompt = f"Pretend I am a person who does not have robust technology literacy and does not know how to make specific and well defined search queries. I look up {user_input}. This is a pretty broad and not well defined search query. My friend asks me the question {follow_up_question}. I give the exact response {user_answer}. Given my response to this question and my original query, give me a 1-3 word phrase that represents the answer to the question but that does not include any of the words from what I originally looked up. I want the 1-3 word phrase to come from the answer itself so USE words from the answer! For example, if the question is 'where is the location of the chest pain' and the answer is 'on the left side' and the original query was 'chest pain’, the output should be ‘left side’. Don't include the words 'possible' or 'output'"
    #prompt = f"A user searches the internet search query \"{user_input}\" and responds \"{user_answer}\" to the clarification question \"{follow_up_question}\". Provide a 2-4 term extension to the original user query \"{user_input}\" that encapsulates this new response. Do not include any punctuation or special characters. DO NOT WRAP ANSWER IN QUOTES"
    response = openai.completions.create( 
        model = "gpt-3.5-turbo-instruct",
        prompt = prompt,
        max_tokens=256,
        temperature=1,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    add_on = response.choices[0].text.strip()
    add_on = remove_common_words(add_on, user_input)

    return user_input + " " + add_on



def get_multiple_choice(question):
        # Find the index of the first '[' and the index of the last ']'
    start_index = question.find('[')
    end_index = question.rfind(']')

    # for malformed responses:
    if start_index == -1:
        start_index = question.find('(')
        end_index = len(question) - 1
    
    # Extract the choices substring
    choices_str = question[start_index + 1:end_index]
    
    # Split the choices string by commas
    choices_list = choices_str.split('*')
    
    # Strip leading and trailing whitespace from each choice
    choices_list = [choice.strip() for choice in choices_list]
    
    # Cropped question
    cropped_question = question[:start_index]
    return choices_list, cropped_question

def prompt_question_with_choices(question, choices):
    print(question)
    for i, choice in enumerate(choices):
        print(f"{choice}")  # Prints A, B, C, D, ... for each choice
        print("\n")
    user_input = input("Your answer: ").strip().upper()  # Prompt user for input
    return user_input
