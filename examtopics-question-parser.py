# Import required modules
from email import header
import re
import random
import requests
from bs4 import BeautifulSoup

# ExamTopics Credentials - CHANGE ME
email = "#####"
password = "#####"

# Set the User-Agent so the site doesnt block the scraping
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"
}

payload = {
    "email": email,
    "password": password
}

# Login with credentials and session to create cookie
r = requests.Session()
r.post("https://www.examtopics.com/login", headers=headers, data=payload)

examProvidersPage = requests.get("https://www.examtopics.com/exams", headers=headers)

# Parse all exam providers from ExamTopics
examProviders = []

examProvidersPage = r.get("https://www.examtopics.com/exams", headers=headers)
examProvidersSoup = BeautifulSoup(examProvidersPage.content, "html.parser") # Soup HTML Parser
examProvidersRaw = examProvidersSoup.find_all("div", class_="provider-list-link") # Select all divs with class provider-list-link

for rawProvider in examProvidersRaw:
    examProvider = {}

    examProviderText = rawProvider.find("a").text
    examProviderText = examProviderText.split("\n")

    # Parse provider title
    examProvider["title"] = examProviderText[0].strip()

    # Parse provider number of exams
    examProvider["exams"] = examProviderText[1].strip()

    # Parse provider link
    examProvider["link"] = rawProvider.find("a")["href"]

    examProviders.append(examProvider)

print("\n"*100)

# Display exam providers
for x in range(len(examProviders)):
    print("[{}] {} {}".format(str(x+1), examProviders[x]["title"], examProviders[x]["exams"]))

providerChoice = int(input("\nPlease select an exam provider: "))
examProvider = examProviders[providerChoice - 1]


# Parse exams from provider selected
exams = []

examsPage = r.get("https://www.examtopics.com"+examProvider["link"], headers=headers)
examsSoup = BeautifulSoup(examsPage.content, "html.parser") # Soup HTML Parser
examsRaw = examsSoup.find_all("a", class_="popular-exam-link") # Select all anchors where the class is popular-exam-link

for rawExam in examsRaw:
    exam = {}

    # Parse exam title
    exam["title"] = rawExam.text.strip()

    # Parse exam link
    exam["link"] = rawExam["href"]

    exams.append(exam)

print("\n"*100)

# Display exams available
for x in range(len(exams)):
    print("[{}] {}".format(str(x+1), exams[x]["title"]))

examChoice = int(input("\nPlease select an exam: "))
exam = exams[examChoice - 1]

# Get questions from exam
examQuestions = []

examQuestionsPage = r.get("https://www.examtopics.com"+exam["link"]+"view", headers=headers)
examQuestionsSoup = BeautifulSoup(examQuestionsPage.content, "html.parser") # Soup HTML Parser
examQuestionsRaw = examQuestionsSoup.find_all("div", class_="exam-question-card") # Select all anchors where the class is popular-exam-link

for examQuestionRaw in examQuestionsRaw:
    examQuestion = {}

    # Get question ID (for cross reference)
    examQuestionIdRaw = examQuestionRaw.find("div", class_="card-header").text
    examQuestion["id"] = re.findall("#[0-9]*", examQuestionIdRaw)[0].strip()

    # Get the body of the question
    examQuestion["body"] = examQuestionRaw.find("p", class_="card-text").text.strip()
    
    # Get question choice
    examQuestionChoicesRaw = examQuestionRaw.find_all("li", class_="multi-choice-item")
    examQuestion["choices"] = [re.sub("\s\s+", " ", choice.text.strip()) for choice in examQuestionChoicesRaw]

    # Get question answer
    examQuestion["answer"] = examQuestionRaw.find("span", class_="correct-answer").text.strip()

    examQuestions.append(examQuestion)

score = 0 
# For each question, print the question number and question.
for x in range(0, len(examQuestions)):
    print("\n"*100)
    print("""
{}/{} ({}).

{}\n""".format(x + 1, len(examQuestions), examQuestions[x]["id"], examQuestions[x]["body"]))

    # Print each choice
    for choice in examQuestions[x]["choices"]:
        print(choice)
    
    answer = input("\n> ")

    # Display correct answer
    print("\n"*100)
    for choice in examQuestions[x]["choices"]:
        print(choice)
    print("""\n
Your input: {}
Correct Answer: {}
    """.format(answer.upper(), examQuestions[x]["answer"]))

    userNext = input("\n(Press enter to continiue)")

    # If correct +1 to score
    if answer.upper() == examQuestions[x]["answer"]:
        score += 1

# Print results
print("\n"*100)
print("Results {}/{}".format(int(score), len(examQuestions)))
