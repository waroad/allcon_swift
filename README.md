모바일앱프로그래밍 2 swift 프로젝트

ALLCON

레포 다운 후, source env/scripts/activate 터미널에 입력 

(가상환경 실행시켜서 필요한 라이브러리를 자동으로 적용해준다.)

cd backend

python manage.py makemigrations

python manage.py migrate

python manage.py runserver

순서대로 터미널에 입력해서 백엔드 서버 실행.


---- 

API DOCUMENT

도메인 주소: http://127.0.0.1:8000/


**USERS 관련:**

|REST 명령어|주소|설명|필요입력값|
|----------|---|---|------------|
|POST|register/|유저 최초 회원가입|username:"a",password:"b",profile:{}|
|POST|api/token/|로그인 여기서 불러온 access 토큰 추후 계속 사용.|username:"a",password:"b"|
|DELETE|delete/|현재 로그인 되어 있는 유저 탈퇴|없음|
|GET|users/current/|현재 로그인 되어 있는 유저의 정보 불러오기|없음|
|PUT|users/<int:pk>/|유저 정보 수정, taste 인 취향만 수정 가능 int:pk 자리에 로그인 된 유저의 id 값 넣기. (username 과 별개로 id 값이 있음)|taste:['a','b']|


**MOVIES 관련:**

|REST 명령어|주소|설명|필요입력값|
|-----------|---|---|----------|
|POST|movies/|영화 상세 페이지 불러오기. 여기서 id 값 잘 저장하기|content:"영화정보-년도", imageURL: 이미지 URL, movieURL: movieURL|
|GET|movies/<int:pk>/|위에서 저장한 id로 영화 상세 페이지 다시 불러오기. 여기서 liked 가 0일 경우 찜을 안한 것이고, 1일 경우 찜을 한 것임|없음|
|GET|movies/<int:pk>/reviews/|해당 영화의 리뷰들 불러오기. 시간 순으로 역순이고, 현재 로그인 한 사용자가 작성한 리뷰가 있다면 제일 첫번째 값으로 불러옴|없음|
|POST|movies/<int:pk>/like/|해당 영화에 찜하기. 이미 짐한 상태에서 또 누르면 찜 해제.|없음|

**REVIEWS 관련:**

|REST 명령어|주소|설명|필요입력값|
|----------|---|---|-----------|
|GET|reviews/|사용자가 작성한 리뷰가 있는 영화 제목들 리턴|없음|
|POST|reviews/|리뷰 작성. |content:"리뷰내용", movieId: "영화의 id 번호", star: "별점"|
|PUT|reviews/<int:pk>|해당 리뷰 수정. 주인만 할 수 있음.|content:"리뷰내용", movieId: "영화의 id 번호", star: "별점"|


**CRAWLING 관련:**

|REST 명령어|주소|설명|필요입력값|
|-----------|---|---|----------|
|GET|search_result/|크롤링을 시도하는 chromewebdriver창을 열고 닫기 위함|state:"open" 또는 "close"|
|POST|search_result/|키워드로 서치하거나 상세페이지를 불러오기 위함|keyword:"콘텐츠 제목" 또는 url:"상세페이지 링크" 둘 중 하나만 보내면 됨|

---
유저 프로파일 설명:

likedMovies: 찜한 영화 목록을 보여줌. 최근에 찜한 것이 앞에 옴 ['영화제목', '이미지URL', '영화URL'] 순으로 저장됨

searchedMovies: 검색한 영화 목록을 보여줌. 최근에 검색한 것이 앞에 옴 ['영화제목', '이미지URL', '영화URL'] 순으로 저장됨

taste: 취향이 들어가 있음. 수정에서 취향 수정할 때 꼭 "['취향1',취향2','취향3']" 형식에 맞춰서 적기

---
