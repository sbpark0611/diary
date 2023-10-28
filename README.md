# 일기 앱

일기를 작성하면 AI가 자동으로 태그를 달아주고 댓글을 달아주는 프로그램.

## 사용법

- https://drive.google.com/file/d/1jI3fxT8YgRTAaP2TBM27vk3h0-qxLbql/view?usp=share_link

- 위의 링크에서 파일을 다운받고 압축을 푼다.

- main.py와 같은 위치에 question_answering 폴더를 놓는다.

- python main.py 커맨드로 실행한다.

- 버튼이나 텍스트 입력 부분이 한번에 안눌리고 여러번 눌러야 하는 문제가 있다.

## 사용된 모델

- [gpt2](https://github.com/openvinotoolkit/open_model_zoo/tree/master/models/public/gpt-2)

- [bert-large-uncased-whole-word-masking-squad](https://github.com/openvinotoolkit/open_model_zoo/tree/master/models/intel/bert-large-uncased-whole-word-masking-squad-0001)

- [bert-base-ner](https://github.com/openvinotoolkit/open_model_zoo/tree/master/models/public/bert-base-ner)

## 상세 설명

### 태그 생성

bert-base-ner, bert-large-uncased-whole-word-masking-squad 모델을 이용했다.

#### Named Entity Recognition

먼저 bert-base-ner로 named entity를 추출했다.

추출된 named entity는 그대로 태그로 입력했다.

#### Question Answering

named entity가 아니어도 중요한 정보를 담고 있을 가능성이 있다.

그러한 정보를 추출하기 위해 bert-large-uncased-whole-word-masking-squad를 사용했다.

demo를 참고해 Question Answering을 할 수 있는 모델을 만들었다.

중요 키워드를 얻을 수 있는 여러 질문을 하고 작성된 일기 안에서 답을 추출한다.

사용된 질문
- "what is the most important part of this paragraph?"
- "what is the topic of the paragraph?"
- "What is the key point in this content?"
- "What is the essential element that I should focus on in this content?"

question answering을 통해 나온 결과물은 길이가 길어 태그에 적합하지 않을 수 있기 때문에 만약 결과가 5단어 이상일 경우 다시 해당 결과 안에서 위의 질문을 통해 중요 키워드를 추출했다.

### 댓글

gpt2 모델을 이용했다.

특정 문자열을 입력하면 이어지는 문자열을 예측하는 모델이다.

일기 내용을 모델에 입력하면 일기를 이어서 작성한 결과가 나온다.

하지만 작성한 일기를 읽고 AI가 위로, 공감, 칭찬 등의 반응을 하기를 바랬다.

따라서 입력된 텍스트를 "[User]: {input_text}\n[AI]: "로 변경했다.

단순히 input_text를 넣었을 때 보다 응답으로 볼 수 있는 결과물이 많아졌다.

하지만 더 높은 성능을 위해서는 질문과 응답 데이터로 fine tuning이 필요할 것 같다.

### 메인 화면

<img width="525" alt="Screenshot 2023-10-28 at 10 27 54 PM" src="https://github.com/sbpark0611/diary/assets/101174826/d2167a7f-fbbe-4727-bf7c-d5d5eb831d3b">

- 일기 보기, 일기 쓰기 두 개의 버튼이 있다.

### 일기 작성

<img width="534" alt="Screenshot 2023-10-28 at 10 21 39 PM" src="https://github.com/sbpark0611/diary/assets/101174826/504ba31a-dc23-4e92-b6be-1ff160c85683">

- 너무 길게 작성하면 모델에서 오류가 난다.

- 모델이 처리하는 시간이 걸린다.

### 일기 리스트 보기

<img width="529" alt="Screenshot 2023-10-28 at 10 29 01 PM" src="https://github.com/sbpark0611/diary/assets/101174826/3ca20e3c-10f0-46bc-9adb-8c39db81a505">

- 일기가 많은 경우 스크롤이 된다.

### 일기 상세 보기

<img width="525" alt="Screenshot 2023-10-28 at 10 30 21 PM" src="https://github.com/sbpark0611/diary/assets/101174826/ce72ca1d-9cfd-4ae7-a81f-8a66083827d4">

- 날짜, 태그, 일기, 댓글을 볼 수 있다.