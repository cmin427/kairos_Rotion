
# 라이브러리
import os
import time
import cv2
import pyautogui
import pandas as pd
import streamlit as st
import speech_recognition as sr

from dotenv import load_dotenv
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import DataFrameLoader
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

# OPENAI API KEY
load_dotenv()
os.environ['OPENAI_API_KEY'] = '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'

# data
df = pd.read_csv('sample_list.csv')
df['combined_info'] = df.apply(lambda row: f"Name: {row['name']}. Character: {row['character']}. Category: {row['category']}. District: {row['district']}. Floor: {row['floor']}. Price: {row['price']}. Feature : {row['feature']}", axis=1)
loader = DataFrameLoader(df, page_content_column="combined_info")
docs  = loader.load()   # document 형식으로 출력
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
texts = text_splitter.split_documents(docs)
embeddings = OpenAIEmbeddings()    # default model='text-embedding-ada-002'
vectorstore  = FAISS.from_documents(texts, embeddings)

# llm
llm = ChatOpenAI(model='gpt-3.5-turbo', temperature=0)      # temperature - llm이 생성하는 텍스트의 다양성을 조절하는 하이퍼파라미터

# prompt
chatbot_template = """ 
You are a friendly, conversational retail shopping assistant that help customers to find product that match their preferences. 
From the following context and chat history, assist customers in finding what they are looking for based on their input. 

1. **Price-related questions**:  
   - If the input is a price-related question about a specific product(e.g. 이 제품은 얼마예요?), provide only the price of the product with a polite explanation in Korean.  
     Example: "해당 상품의 가격은 17,500원입니다."  
   - Do not include a recommendation list.

2. **Product purchase intent**:  
   - If the user explicitly expresses an intent to purchase a specific product(e.g. the input contains phrases like "구매할게요", "살게요", "사고싶어요"), provide the location of the product (district and floor) in polite Korean.  
     Example: "해당 상품은 C구역 1층에 있어요. 구매를 원하시면 구매 버튼을 누르고 제품 이름을 말해주세요!"
   - Do not interpret general product inquiries like "어떤 제품이 있나요?" or "이 제품 찾고 있어요" as a purchase intent.

3. **General product inquiries**:  
    - If the user specifies a brand, recommend only products from that brand. Do not include products from other brands.  
    - If the user does not specify a brand, recommend products that best match the described characteristics.
    
4. **Unknown answers**:  
   - If you don't know the answer, just say that you don't know, and don't try to make up an answer.


{context}

chat history: {history}

input: {question} 
Your Response:

"""
chatbot_prompt = PromptTemplate(
    input_variables=["context","history","question"],
    template=chatbot_template,
)

# chain
memory = ConversationBufferMemory(memory_key="history", input_key="question", return_messages=True)

qa = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type='stuff',
    retriever=vectorstore.as_retriever(),
    verbose=False,
    chain_type_kwargs={
        "verbose": False,
        "prompt": chatbot_prompt,
        "memory": memory}
)

def find_name(name, df):
    df_copy = df.copy()
    df_copy.loc[len(df_copy),'name'] = name     # name 컬럼에 추가
    
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform(df_copy['name'])   # tf-idf 행렬
    cosine_sim = cosine_similarity(vectors, vectors)    # 코사인 유사도
    
    idx = len(df_copy)-1     # user가 입력한 name의 index
    sim_scores = list(enumerate(cosine_sim[idx]))   # 모든 제품과의 유사도
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1]      # 제일 유사한 제품
    product_name = df_copy['name'].iloc[sim_scores[0]]

    return product_name

def recording():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.write('Listening...')
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source) 
        try:    # 구글 웹 스피치 api (하루에 50개 제한)
            text = r.recognize_google(audio, language='ko')
            st.session_state.recorded = False
            return text
        except sr.UnknownValueError:    # 인식되지 않은 경우
            return '다시 말해주세요.'
        except sr.RequestError as e:
            return '작동되지 않았습니다. 오류코드: {0}'.format(e)
        
# image load
wait_img = cv2.imread("robot_image.jpg")
wait_img = cv2.cvtColor(wait_img, cv2.COLOR_BGR2RGB)
end_img = cv2.imread("end_image.jpg")
end_img = cv2.cvtColor(end_img, cv2.COLOR_BGR2RGB)

### streamlit app
st.set_page_config(page_title='chatbot')

if 'show_img' not in st.session_state:
    st.session_state.show_img = True

if 'clicked' not in st.session_state:
    st.session_state.recommend = False

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'finish' not in st.session_state:    # 안내 종료 신호 받기
    st.session_state.finish = False

if 'recorded' not in st.session_state:
    st.session_state.recorded = False

if 'chat_end' not in st.session_state:
    st.session_state.chat_end = False

placeholder = st.empty()

if st.session_state.show_img:
    with placeholder.container():
        st.image(wait_img, use_container_width=True)
        with st.spinner('Loading...'):
            time.sleep(2)
            st.session_state.show_img = False
            placeholder.empty()

if not st.session_state.show_img and not st.session_state.chat_end:
    with placeholder.container():
        st.title('🤖 Robotics Revolution ')
        st.markdown("<div style='margin: 30px 0;'></div>", unsafe_allow_html=True)  # 여백추가
        st.markdown("""**안녕하세요! 어떤 상품을 찾으시나요?   
                        찾는 상품의 이름이나 키워드를 말씀해주세요.**   
                        *(ex. 춘식이 그려진 제품 있나요?, 무드등 추천해주세요. )*""")
        st.markdown("<div style='margin: 30px 0;'></div>", unsafe_allow_html=True)  

        btn = st.button('🎙️')

        if btn:
            if not st.session_state.recorded:
                st.session_state.recorded = True
                user_input = recording()
                if user_input:
                    st.session_state.messages.append({'role': 'user', 'content': user_input})
                    answer = qa.invoke(user_input)
                    st.session_state.messages.append({'role': 'assistant', 'content': answer['result']})
                st.session_state.recorded = False

        for message in st.session_state.messages:
            if message['role'] == 'user':
                st.chat_message('user').markdown(message['content'])
            elif message['role'] == 'assistant':
                st.chat_message('assistant').markdown(message['content'])

        if st.button('구매 🛒'):
            st.session_state.clicked = True
            if not st.session_state.recorded:
                st.session_state.recorded = True
                while True:
                    product_name = recording()
                    if product_name:
                        try:
                            name = find_name(product_name,df)
                        except:
                            st.warning("제품을 찾을 수 없습니다. 다시 시도해 주세요.")
                    if name is not None:
                        break

                if name:
                    district = df[df['name']==name]['district'].values[0]
                    floor = df[df['name']==name]['floor'].values[0]
                    st.markdown(f"""제품명 : {name}   
                                    위치 : {district}구역 {floor}층   
                                    **안내를 시작합니다!**
                    """)
                    with open('info.txt', 'w') as file:     # 안내할 제품 정보 저장
                        data = f'{name}|{district}|{floor}'
                        file.write(data)

                    time.sleep(2)
                    placeholder.empty()
                    time.sleep(1)
                    st.session_state.chat_end = True
                st.session_state.recorded = False

if st.session_state.chat_end:   # 안내 멘트 이후
    # placeholder.empty()
    
    while True:
        with placeholder.container():   # 기본 대기 이미지
            st.image(wait_img, use_container_width=True)
            
        try:    # 종료 신호 확인
            with open('done.txt', 'r') as f:
                value = int(f.read().strip())

                if value == 1:      # 상품 위치 도착
                    with placeholder.container():   # 안내 종료 이미지
                        st.image(end_img, use_container_width=True)
                    time.sleep(10)

                    placeholder.empty()
                    time.sleep(1)

                    with placeholder.container():   # 기본 이미지
                        st.image(wait_img, use_container_width=True)
                    
                    while True:     # value가 0이 되기 전까지 이미지 유지
                        with open('done.txt', 'r') as f:
                            value = int(f.read().strip())
                        if value == 0:
                            break
                        time.sleep(1)

                elif value == 0:    # 초기 위치 도착
                    st.session_state.finish = True
        except:
            pass

        if st.session_state.finish:
            time.sleep(1)
            pyautogui.hotkey('ctrl', 'w')   # 종료
