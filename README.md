# 일기 앱

- 일기를 작성하면 AI가 자동으로 태그를 달아주고 댓글을 달아주는 프로그램.

## 사용법

- https://drive.google.com/file/d/1jI3fxT8YgRTAaP2TBM27vk3h0-qxLbql/view?usp=share_link

- 위의 링크에서 파일을 다운받고 압축을 푼다.

- main.py와 같은 위치에 question_answering 폴더를 놓는다.

- python main.py 커맨드로 실행한다.

- 버튼이나 텍스트 입력 부분이 한번에 안눌리고 여러번 눌러야 하는 문제가 있다.

## 사용된 모델

- [gpt2](https://github.com/openvinotoolkit/open_model_zoo/tree/master/models/public/gpt-2)

- [bert-large-uncased-whole-word-masking-squad-0001](https://github.com/openvinotoolkit/open_model_zoo/tree/master/models/intel/bert-large-uncased-whole-word-masking-squad-0001)

- [bert-base-ner](https://github.com/openvinotoolkit/open_model_zoo/tree/master/models/public/bert-base-ner)

## 상세 설명



### 메인 화면
<img width="525" alt="Screenshot 2023-10-28 at 10 27 54 PM" src="https://github.com/sbpark0611/diary/assets/101174826/d2167a7f-fbbe-4727-bf7c-d5d5eb831d3b">
- 일기 보기, 일기 쓰기 두 개의 버튼이 있다.

### 일기 작성
<img width="528" alt="Screenshot 2023-10-28 at 10 28 45 PM" src="https://github.com/sbpark0611/diary/assets/101174826/8c70a7aa-b91e-4f20-9de8-22be242153ce">
- 너무 길게 작성하면 모델에서 오류가 난다.

### 일기 리스트 보기
<img width="529" alt="Screenshot 2023-10-28 at 10 29 01 PM" src="https://github.com/sbpark0611/diary/assets/101174826/3ca20e3c-10f0-46bc-9adb-8c39db81a505">
- 일기가 많은 경우 스크롤이 된다.

### 일기 상세 보기
<img width="525" alt="Screenshot 2023-10-28 at 10 30 21 PM" src="https://github.com/sbpark0611/diary/assets/101174826/ce72ca1d-9cfd-4ae7-a81f-8a66083827d4">
- 날짜, 태그, 일기, 댓글을 볼 수 있다.

## 아쉬운 점

- UI가 굉장히 사용하기 불편하고 예쁘지 않다.

- 모델의 성능이 낮다. 특히 gpt2를 이용한 댓글이 정상적으로 달리지 않는다. 
    - 여러 방법을 시도해봤지만 성능을 올리기 위해서는 결국 fine tuning이 필요할 듯 하다.