# chatbot_service.py - 동적 Few-shot 적용된 챗봇 서비스

import hashlib
import json
import os
from datetime import datetime
from typing import Any, Dict, List

# Django imports
from django.conf import settings
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
# LangChain imports
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.retrievers import MultiQueryRetriever
from langchain.schema import Document
from langchain.vectorstores import Chroma

from app.knowledge_document.models import BlogPost, ChatLog, ChromaVector, CompanyContent, Project


class CompanyChatbotService:
    """회사 챗봇 서비스 - 동적 Few-shot Learning 적용"""

    def __init__(self):
        # OpenAI 설정
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        # self.llm = ChatOpenAI(openai_api_key=settings.OPENAI_API_KEY, model="gpt-3.5-turbo", temperature=0.1)
        self.llm = ChatOpenAI(openai_api_key=settings.OPENAI_API_KEY, model="gpt-4o", temperature=0.1)

        # Chroma 벡터스토어 설정
        self.vector_store = Chroma(
            collection_name="company_knowledge", embedding_function=self.embeddings, persist_directory="./chroma_db"
        )

        # Few-shot 예시들 설정
        self.setup_few_shot_examples()

    def setup_few_shot_examples(self):
        """질문 유형별 Few-shot 예시 설정"""

        # 회사 소개 관련 예시
        self.company_examples = [
            {
                "question": "이 회사는 뭐하는 회사인가요?",
                "answer": """안녕하세요! 저희 똑똑한개발자는 혁신적인 IT 솔루션을 제공하는 개발 전문 회사입니다.

🏢 **회사 개요**
- 설립: 2020년 (4년차 성장 기업)
- 전문분야: 웹/앱 개발, AI 솔루션, 클라우드 서비스
- 팀 구성: 시니어 개발자 중심의 전문 인력

💡 **핵심 강점**
- 최신 기술 스택 기반 개발
- 고객 맞춤형 솔루션 제공
- 빠른 개발 주기와 안정적인 운영

🎯 **주요 고객층**
- 스타트업부터 중견기업까지
- 디지털 전환이 필요한 기업들""",
            },
            {
                "question": "팀 구성은 어떻게 되나요?",
                "answer": """저희 팀은 각 분야별 전문가들로 구성되어 있습니다.

👥 **팀 구성**
- **개발팀 (17명)**: 풀스택, 프론트엔드, 백엔드 전문가
- **디자인팀 (8명)**: UI/UX, 그래픽 디자인
- **기획팀 (4명)**: 프로젝트 매니저

🌟 **팀의 특징**
- 평균 경력 5년+ 시니어 개발자 중심
- 애자일 방법론 기반 협업
- 지속적인 기술 학습과 공유 문화""",
            },
        ]

        # 프로젝트 관련 예시
        self.project_examples = [
            {
                "question": "어떤 프로젝트를 진행했나요?",
                "answer": """다양한 분야의 혁신적인 프로젝트들을 성공적으로 완료했습니다.

🌟 **대표 프로젝트**

**💰 핀테크 플랫폼**
- 개발기간: 8개월, 팀 규모: 6명
- 기술스택: React, Django, PostgreSQL, Redis
- 주요기능: 간편결제, 자산관리, 투자상품 연동

**🛒 이커머스 솔루션**
- 개발기간: 6개월, 팀 규모: 5명  
- 기술스택: Vue.js, FastAPI, MongoDB
- 주요기능: 상품관리, 주문결제, 재고관리, 분석대시보드

**🤖 AI 챗봇 시스템**
- 개발기간: 4개월, 팀 규모: 4명
- 기술스택: Python, LangChain, OpenAI API, Chroma
- 주요기능: 자연어 처리, 문서 검색, 학습 기능""",
            },
            {
                "question": "포트폴리오 하이라이트를 보여주세요",
                "answer": """저희의 대표적인 성공 사례들을 소개해드리겠습니다.

🏆 **포트폴리오 하이라이트**

**1. 스마트 물류 관리 시스템**
- 대기업 계열사 프로젝트
- 개발기간: 10개월, 투입인력: 8명
- 성과: 업무 효율성 40% 향상, 비용 절감 30%

**2. 헬스케어 모바일 앱**
- 의료진-환자 연결 플랫폼
- 월 활성 사용자 50,000명 돌파
- 앱스토어 평점 4.8점 유지

**3. 교육 플랫폼 구축**
- 온라인 학습 관리 시스템
- 동시 접속자 10,000명 처리 가능
- 실시간 화상 수업 기능 구현""",
            },
        ]

        # 기술 스택 관련 예시
        self.tech_examples = [
            {
                "question": "React 개발 가능한가요?",
                "answer": """네! React는 저희의 핵심 프론트엔드 기술입니다.

⚛️ **React 전문 역량**
- **경험**: 3년+ 실무 경험, 10개+ 프로덕션 프로젝트
- **관련 기술**: Next.js, TypeScript, Redux Toolkit, React Query
- **프로젝트 규모**: 소규모 랜딩페이지부터 대규모 SPA까지

🛠️ **개발 전문성**
- 성능 최적화 (Code Splitting, Lazy Loading)
- 반응형 디자인 및 크로스브라우징
- 테스트 코드 작성 (Jest, React Testing Library)
- 상태 관리 패턴 설계

📈 **최근 React 프로젝트**
- 핀테크 대시보드 (TypeScript + Next.js)
- 실시간 채팅 앱 (Socket.io 연동)
- 관리자 페이지 (Material-UI 활용)""",
            },
            {
                "question": "백엔드 개발은 어떤 기술을 사용하나요?",
                "answer": """다양한 백엔드 기술 스택으로 안정적인 서버를 구축합니다.

🔧 **주요 백엔드 기술**

**Python 생태계**
- Django REST Framework (API 서버)
- FastAPI (고성능 비동기 API)
- Celery (백그라운드 작업 처리)

**Node.js 생태계**  
- Express.js (빠른 프로토타이핑)
- NestJS (엔터프라이즈급 애플리케이션)

**데이터베이스**
- PostgreSQL (관계형 DB)
- MongoDB (NoSQL)
- Redis (캐싱, 세션 관리)

☁️ **클라우드 & 인프라**
- AWS (EC2, RDS, S3, Lambda)
- Docker 컨테이너화
- CI/CD 파이프라인 구축""",
            },
        ]

        # 일반적인/기타 예시
        self.general_examples = [
            {
                "question": "견적 문의는 어떻게 하나요?",
                "answer": """프로젝트 견적 문의는 여러 방법으로 가능합니다.

📞 **견적 문의 방법**
- **이메일**: contact@toktokhan.dev
- **전화**: 02-1234-5678 (평일 9시-18시)
- **카카오톡**: @똑똑한개발자
- **홈페이지**: 온라인 견적 문의 폼 작성

📋 **견적에 필요한 정보**
- 프로젝트 개요 및 목적
- 주요 기능 요구사항
- 예상 일정 및 예산 범위
- 참고 사이트나 앱이 있다면

⏰ **견적 제공 일정**
- 간단한 프로젝트: 1-2일 내
- 복잡한 프로젝트: 3-5일 내 상세 제안서 제공

💡 **무료 컨설팅**
- 초기 기획 단계 무료 상담 가능
- 기술 스택 추천 및 아키텍처 설계 조언""",
            }
        ]

    def _analyze_question_type(self, question: str) -> str:
        """점수 기반 질문 유형 분석 - 복합 질문 처리 개선"""
        question_lower = question.lower()

        # 점수 초기화
        scores = {"company": 0.0, "project": 0.0, "tech": 0.0, "general": 0.0}

        # 키워드별 가중치 매핑 (기존 키워드 + 가중치)
        keyword_weights = {
            "company": {
                "회사": 1.0,
                "기업": 1.0,
                "팀": 0.8,
                "조직": 0.8,
                "소개": 0.6,
                "설립": 0.8,
                "직원": 0.7,
                "구성원": 0.7,
                "문화": 0.6,
            },
            "project": {
                "프로젝트": 2.0,
                "포트폴리오": 1.8,
                "개발": 1.2,
                "진행": 1.0,
                "경험": 0.8,
                "사례": 1.2,
                "구축": 1.3,
                "제작": 1.2,
                "완료": 1.0,
                "진행했던": 1.5,
                "진행한": 1.5,
                "작업": 0.8,
                "업무": 0.8,
            },
            "tech": {
                # 구체적 기술명 (높은 가중치)
                "react": 2.0,
                "vue": 2.0,
                "angular": 2.0,
                "javascript": 1.8,
                "typescript": 1.8,
                "python": 2.0,
                "django": 2.0,
                "fastapi": 1.8,
                "node": 1.8,
                "express": 1.8,
                "spring": 1.8,
                "java": 1.8,
                "php": 1.8,
                "laravel": 1.8,
                "mysql": 1.5,
                "postgresql": 1.5,
                "mongodb": 1.5,
                "redis": 1.5,
                "aws": 1.8,
                "docker": 1.8,
                "kubernetes": 1.8,
                # 일반 기술 용어
                "기술": 1.0,
                "스택": 1.2,
                "언어": 1.0,
                "프레임워크": 1.2,
                "데이터베이스": 1.0,
                "클라우드": 1.0,
                "인프라": 1.0,
            },
        }

        # 기본 키워드 점수 계산
        for category, keywords in keyword_weights.items():
            for keyword, weight in keywords.items():
                if keyword in question_lower:
                    scores[category] += weight

        # 특별 패턴 보너스 점수
        self._apply_pattern_bonuses(question_lower, scores)

        # 복합 질문 처리 로직
        return self._determine_final_type(scores, question_lower)

    def _apply_pattern_bonuses(self, question_lower: str, scores: dict):
        """질문 패턴에 따른 보너스 점수 적용"""

        # 프로젝트 질문 패턴
        project_patterns = [
            ("로 진행한", 1.5),
            ("로 개발한", 1.5),
            ("을 사용한", 1.2),
            ("로 만든", 1.3),
            ("기술로", 1.0),
            ("스택으로", 1.0),
            ("프로젝트 중에", 1.8),
            ("포트폴리오", 1.5),
            ("진행했던", 1.3),
            ("개발했던", 1.3),
            ("어떤 프로젝트", 1.5),
        ]

        for pattern, bonus in project_patterns:
            if pattern in question_lower:
                scores["project"] += bonus

        # 기술 질문 패턴
        tech_patterns = [
            ("가능한가요", 1.5),
            ("할 수 있나요", 1.5),
            ("할 수 있어요", 1.5),
            ("개발 가능", 1.5),
            ("기술 스택", 1.3),
            ("사용하나요", 1.2),
            ("경험이 있나요", 1.3),
            ("경험이 있어요", 1.3),
            ("다룰 수 있나요", 1.4),
            ("어떤 기술", 1.2),
            ("어떤 언어", 1.2),
            ("백엔드", 1.2),
            ("프론트엔드", 1.2),
        ]

        for pattern, bonus in tech_patterns:
            if pattern in question_lower:
                scores["tech"] += bonus

        # 회사 질문 패턴
        company_patterns = [
            ("뭐하는 회사", 2.0),
            ("어떤 회사", 1.5),
            ("회사 소개", 1.8),
            ("팀 구성", 1.5),
            ("회사 문화", 1.5),
            ("조직 구성", 1.3),
        ]

        for pattern, bonus in company_patterns:
            if pattern in question_lower:
                scores["company"] += bonus

    def _determine_final_type(self, scores: dict, question_lower: str) -> str:
        """최종 질문 유형 결정"""

        # 디버깅을 위한 점수 출력 (필요시 주석 해제)
        # print(f"점수 분석: {scores}")

        # 최고 점수 카테고리들 찾기
        max_score = max(scores.values())

        # 모든 점수가 0인 경우
        if max_score == 0:
            return "general"

        # 최고 점수를 가진 카테고리들
        top_categories = [cat for cat, score in scores.items() if score == max_score]

        # 동점인 경우 우선순위 적용
        if len(top_categories) > 1:
            return self._resolve_tie(top_categories, scores, question_lower)

        return top_categories[0]

    def _resolve_tie(self, tied_categories: list, scores: dict, question_lower: str) -> str:
        """동점 시 우선순위 결정"""

        # 우선순위 규칙
        priority_rules = [
            # 1순위: tech + project 조합 → 구체적 기술 언급 여부로 결정
            (["tech", "project"], self._tech_project_resolver),
            # 2순위: company + project 조합 → project 우선 (실제 정보 요청)
            (["company", "project"], lambda q: "project"),
            # 3순위: company + tech 조합 → tech 우선 (구체적 역량 문의)
            (["company", "tech"], lambda q: "tech"),
            # 4순위: 전체 동점 → project 우선 (가장 구체적 정보)
            (["company", "project", "tech"], lambda q: "project"),
        ]

        for rule_categories, resolver in priority_rules:
            if set(tied_categories) == set(rule_categories):
                if callable(resolver):
                    return resolver(question_lower)
                else:
                    return resolver

        # 기본값: 알파벳 순서로 첫 번째
        return sorted(tied_categories)[0]

    def _tech_project_resolver(self, question_lower: str) -> str:
        """tech vs project 동점 시 결정 로직"""

        # 구체적 기술명이 많이 언급된 경우 → tech
        specific_techs = ["react", "vue", "angular", "django", "python", "node", "java"]
        tech_mentions = sum(1 for tech in specific_techs if tech in question_lower)

        # 프로젝트 관련 동사가 있는 경우 → project
        project_verbs = ["진행", "개발", "만든", "구축", "제작", "완료"]
        project_verb_mentions = sum(1 for verb in project_verbs if verb in question_lower)

        if tech_mentions >= 2:  # 기술명 2개 이상 → tech 우선
            return "tech"
        elif project_verb_mentions > 0:  # 프로젝트 동사 있음 → project 우선
            return "project"
        else:
            return "project"  # 기본값: project (더 구체적 정보)

    # 구버전
    # def _analyze_question_type(self, question: str) -> str:
    #     """질문 유형 분석"""
    #     question_lower = question.lower()
    #
    #     # 회사 관련 키워드
    #     company_keywords = ["회사", "기업", "팀", "조직", "소개", "설립", "직원", "구성원", "문화"]
    #
    #     # 프로젝트 관련 키워드
    #     project_keywords = ["프로젝트", "포트폴리오", "개발", "진행", "경험", "사례", "구축", "제작", "완료"]
    #
    #     # 기술 관련 키워드
    #     tech_keywords = [
    #         "react",
    #         "vue",
    #         "angular",
    #         "javascript",
    #         "typescript",
    #         "python",
    #         "django",
    #         "fastapi",
    #         "node",
    #         "express",
    #         "spring",
    #         "java",
    #         "php",
    #         "laravel",
    #         "mysql",
    #         "postgresql",
    #         "mongodb",
    #         "redis",
    #         "aws",
    #         "docker",
    #         "kubernetes",
    #         "기술",
    #         "스택",
    #         "언어",
    #         "프레임워크",
    #         "데이터베이스",
    #         "클라우드",
    #         "인프라",
    #         "개발",
    #     ]
    #
    #     # 키워드 매칭으로 질문 유형 판단
    #     if any(keyword in question_lower for keyword in company_keywords):
    #         return "company"
    #     elif any(keyword in question_lower for keyword in project_keywords):
    #         return "project"
    #     elif any(keyword in question_lower for keyword in tech_keywords):
    #         return "tech"
    #     else:
    #         return "general"

    def _get_examples_by_question_type(self, question_type: str) -> List[Dict]:
        """질문 유형별 예시 반환"""
        examples_map = {
            "company": self.company_examples,
            "project": self.project_examples,
            "tech": self.tech_examples,
            "general": self.general_examples,
        }
        return examples_map.get(question_type, self.general_examples)

    def _build_few_shot_prompt(self, question: str, context: str) -> str:
        """동적 Few-shot 프롬프트 생성"""

        # 질문 유형 분석
        question_type = self._analyze_question_type(question)
        examples = self._get_examples_by_question_type(question_type)

        # Few-shot 예시 구성
        examples_text = ""
        for i, example in enumerate(examples[:2], 1):  # 최대 2개 예시 사용
            examples_text += f"""
예시 {i}:
질문: "{example['question']}"
답변: {example['answer']}

"""

        # 최종 프롬프트 구성
        prompt = f"""당신은 똑똑한개발자의 전문 AI 상담원입니다. 아래 예시들을 참고하여 비슷한 형식으로 답변해주세요.

{examples_text}

# 답변 가이드라인
1. 친근하고 전문적인 톤 유지
2. 구체적인 정보와 데이터 포함  
3. 이모지를 활용한 가독성 향상
4. 구조화된 답변 형식 사용
5. 관련 블로그가 있다면 "📝 관련 블로그" 섹션 추가

# 📝 마크다운 포맷팅 규칙 (중요!)
1. **목록 작성 시**: 하이픈(-) 또는 숫자(1.) 사용, • 기호 사용 금지
2. **강조**: **굵은 글씨** 사용
3. **구조**: ## 대제목, **소제목** 형식
4. **목록 예시**:
   - 항목 1: 설명
   - 항목 2: 설명
   또는
   1. 첫 번째 항목
   2. 두 번째 항목

# ⚠️ 중요한 답변 규칙
1. **검색된 정보에만 기반하여 답변** - 없는 정보는 절대 생성하지 마세요
2. 관련 정보가 없으면 "죄송하지만 해당 분야 관련 프로젝트 정보가 없습니다"라고 솔직하게 답변
3. 추측이나 가정으로 답변하지 마세요
4. 정보가 부족하면 문의 방법을 안내해주세요

# 예시 - 정보가 없는 경우:
Q: "블록체인 개발 경험이 있나요?"
A: 죄송합니다. 현재 저희가 보유한 자료에는 블록체인 관련 프로젝트 정보가 없습니다. 

더 자세한 정보가 필요하시다면 아래로 문의해주세요:
📞 **문의 방법**
- 이메일: contact@toktokhan.dev  
- 전화: 02-1234-5678

# 현재 검색된 회사 정보
{context}

# 사용자 질문
{question}

답변:"""

        return prompt

    def _generate_final_answer(self, question: str, context_info: Dict, related_blogs: List) -> str:
        """동적 Few-shot을 적용한 최종 답변 생성"""

        # 동적 Few-shot 프롬프트 생성
        prompt_text = self._build_few_shot_prompt(question, context_info["context_text"])

        # 블로그 섹션 추가
        if related_blogs:
            blog_section = "\n\n# 답변에 포함할 관련 블로그\n"
            for blog in related_blogs:
                blog_section += f"- [{blog['title']}]({blog['url']})\n"
            prompt_text += blog_section

        # ChatGPT 호출
        messages = [{"role": "user", "content": prompt_text}]
        response = self.llm.invoke(messages)

        return response.content

    # 기존 메서드들은 그대로 유지...
    def embed_all_content(self):
        """모든 컨텐츠를 크로마에 임베딩"""
        print("🔄 모든 컨텐츠 임베딩 시작...")

        # 1. 회사 컨텐츠 임베딩
        company_contents = CompanyContent.objects.filter(is_active=True)
        for content in company_contents:
            self._embed_company_content(content)

        # 2. 프로젝트 임베딩
        projects = Project.objects.all()
        for project in projects:
            self._embed_project(project)

        # 3. 블로그 포스트 임베딩
        blog_posts = BlogPost.objects.filter(is_active=True)
        for blog_post in blog_posts:
            self._embed_blog_post(blog_post)

        print("✅ 임베딩 완료!")

    def _embed_company_content(self, content: CompanyContent):
        """회사 컨텐츠 임베딩"""
        embed_text = f"""
        제목: {content.title}
        유형: {content.get_content_type_display()}
        카테고리: {content.category.name}
        내용: {content.content}
        태그: {', '.join(content.tags)}
        검색키워드: {content.search_keywords}
        """

        metadata = {
            "source_type": "company_content",
            "content_id": str(content.id),
            "title": content.title,
            "content_type": content.content_type,
            "category": content.category.name,
            "priority": content.priority,
            "is_featured": content.is_featured,
            "tags": ", ".join(content.tags) if content.tags else "",
        }

        document = Document(page_content=embed_text, metadata=metadata)
        vector_id = f"company_{content.id}"
        self.vector_store.add_documents([document], ids=[vector_id])

        ChromaVector.objects.update_or_create(
            content_type="company_content",
            content_id=content.id,
            defaults={
                "vector_id": vector_id,
                "collection_name": "company_knowledge",
                "source_content_hash": self._get_content_hash(embed_text),
                "needs_update": False,
            },
        )

    def _embed_project(self, project: Project):
        """프로젝트 임베딩"""
        embed_text = f"""
        프로젝트명: {project.name}
        프로젝트 유형: {project.get_project_type_display()}
        클라이언트: {project.client_name}
        설명: {project.description}
        주요 기능: {', '.join(project.key_features)}
        사용 기술: {', '.join(project.technologies_used)}
        팀 크기: {project.team_size}명
        개발 기간: {project.duration_months}개월
        상태: {project.get_status_display()}
        포트폴리오 대표: {'예' if project.is_portfolio_highlight else '아니오'}
        검색태그: {', '.join(project.search_tags)}
        """

        metadata = {
            "source_type": "project",
            "content_id": str(project.id),
            "project_name": project.name,
            "project_type": project.project_type,
            "client_name": project.client_name,
            "technologies": ", ".join(project.technologies_used) if project.technologies_used else "",
            "is_highlight": project.is_portfolio_highlight,
            "duration_months": project.duration_months,
            "team_size": project.team_size,
        }

        document = Document(page_content=embed_text, metadata=metadata)
        vector_id = f"project_{project.id}"
        self.vector_store.add_documents([document], ids=[vector_id])

        ChromaVector.objects.update_or_create(
            content_type="project",
            content_id=project.id,
            defaults={
                "vector_id": vector_id,
                "collection_name": "company_knowledge",
                "source_content_hash": self._get_content_hash(embed_text),
                "needs_update": False,
            },
        )

    def _embed_blog_post(self, blog_post: BlogPost):
        """블로그 포스트 임베딩"""
        embed_text = f"""
        블로그 제목: {blog_post.title}
        발췌: {blog_post.excerpt}
        내용 요약: {blog_post.content_summary}
        관련 주제: {', '.join(blog_post.related_topics)}
        URL: {blog_post.url}
        """

        metadata = {
            "source_type": "blog_post",
            "content_id": str(blog_post.id),
            "title": blog_post.title,
            "url": blog_post.url,
            "related_topics": ", ".join(blog_post.related_topics) if blog_post.related_topics else "",
            "is_featured": blog_post.is_featured,
            "published_date": blog_post.published_date.isoformat() if blog_post.published_date else None,
        }

        document = Document(page_content=embed_text, metadata=metadata)
        vector_id = f"blog_{blog_post.id}"
        self.vector_store.add_documents([document], ids=[vector_id])

        ChromaVector.objects.update_or_create(
            content_type="blog_post",
            content_id=blog_post.id,
            defaults={
                "vector_id": vector_id,
                "collection_name": "company_knowledge",
                "source_content_hash": self._get_content_hash(embed_text),
                "needs_update": False,
            },
        )

    def process_question(self, user_question: str, session_id: str = None) -> Dict[str, Any]:
        """사용자 질문 처리 메인 함수 - 동적 Few-shot 적용"""
        start_time = datetime.now()

        print(f"📝 사용자 질문: {user_question}")

        # 질문 유형 분석
        question_type = self._analyze_question_type(user_question)
        print(f"🎯 질문 유형: {question_type}")

        # 질문 전처리
        processed_question = self._preprocess_question(user_question)
        print(f"🔄 전처리된 질문: {processed_question}")

        # 벡터 검색으로 관련 문서 찾기
        relevant_docs = self._retrieve_relevant_documents(processed_question)
        print(f"🔍 검색된 문서 수: {len(relevant_docs)}")

        # 검색 결과 분석 및 컨텍스트 구성
        context_info = self._analyze_search_results(relevant_docs, user_question)
        print(f"📊 컨텍스트 정보: {context_info['summary']}")

        # 관련 블로그 포스트 찾기
        related_blogs = self._find_related_blogs(context_info, user_question)
        print(f"📝 관련 블로그 수: {len(related_blogs)}")

        # 동적 Few-shot 적용하여 AI 답변 생성
        final_answer = self._generate_final_answer(user_question, context_info, related_blogs)

        # 결과 로깅
        response_time = (datetime.now() - start_time).total_seconds() * 1000
        chat_log = self._log_conversation(
            user_question, processed_question, context_info, related_blogs, final_answer, response_time, session_id
        )

        return {
            "answer": final_answer,
            "related_blogs": related_blogs,
            "sources_used": context_info["sources"],
            "response_time_ms": response_time,
            "chat_log_id": str(chat_log.id),
            "question_type": question_type,  # 디버깅용
        }

    # 나머지 메서드들 (기존과 동일)
    def _preprocess_question(self, question: str) -> str:
        processed = question.strip()
        keyword_mapping = {
            "프로젝트": ["프로젝트", "포트폴리오", "개발", "작업", "업무"],
            "기술": ["기술", "스택", "언어", "프레임워크", "도구"],
            "회사": ["회사", "기업", "조직", "팀"],
        }
        for key, synonyms in keyword_mapping.items():
            if key in processed:
                processed += f" {' '.join(synonyms)}"
        return processed

    def _retrieve_relevant_documents(self, question: str, k: int = 10) -> List[Document]:
        retriever = MultiQueryRetriever.from_llm(
            retriever=self.vector_store.as_retriever(search_kwargs={"k": k}), llm=self.llm
        )
        try:
            documents = retriever.get_relevant_documents(question)
            return documents
        except Exception as e:
            print(f"⚠️ MultiQuery 검색 실패, 기본 검색으로 대체: {e}")
            return self.vector_store.similarity_search(question, k=k)

    def _analyze_search_results(self, documents: List[Document], question: str) -> Dict[str, Any]:
        company_contents = []
        projects = []
        blog_posts = []

        for doc in documents:
            source_type = doc.metadata.get("source_type")
            content_id = doc.metadata.get("content_id")

            if source_type == "company_content":
                try:
                    content = CompanyContent.objects.get(id=content_id)
                    company_contents.append(content)
                except CompanyContent.DoesNotExist:
                    continue
            elif source_type == "project":
                try:
                    project = Project.objects.get(id=content_id)
                    projects.append(project)
                except Project.DoesNotExist:
                    continue
            elif source_type == "blog_post":
                try:
                    blog = BlogPost.objects.get(id=content_id)
                    blog_posts.append(blog)
                except BlogPost.DoesNotExist:
                    continue

        if any(keyword in question.lower() for keyword in ["프로젝트", "포트폴리오", "개발", "진행"]):
            highlight_projects = Project.objects.filter(is_portfolio_highlight=True).exclude(
                id__in=[p.id for p in projects]
            )[:3]
            projects.extend(highlight_projects)

        context_text = self._build_context_text(company_contents, projects, blog_posts)

        return {
            "company_contents": company_contents,
            "projects": projects,
            "blog_posts": blog_posts,
            "context_text": context_text,
            "sources": [doc.metadata for doc in documents],
            "summary": f"회사정보 {len(company_contents)}개, 프로젝트 {len(projects)}개, 블로그 {len(blog_posts)}개 검색됨",
        }

    def _build_context_text(self, company_contents, projects, blog_posts) -> str:
        context_parts = []

        if company_contents:
            context_parts.append("## 회사 정보")
            for content in company_contents[:3]:
                context_parts.append(f"**{content.title}**")
                context_parts.append(content.content[:500] + "...")
                context_parts.append("")

        if projects:
            context_parts.append("## 프로젝트 포트폴리오")
            for project in projects[:5]:
                context_parts.append(f"**{project.name}** ({project.get_project_type_display()})")
                context_parts.append(f"클라이언트: {project.client_name}")
                context_parts.append(f"설명: {project.description[:300]}...")
                context_parts.append(f"기술스택: {', '.join(project.technologies_used)}")
                context_parts.append(f"기간: {project.duration_months}개월, 팀: {project.team_size}명")
                if project.is_portfolio_highlight:
                    context_parts.append("🌟 포트폴리오 대표 프로젝트")
                context_parts.append("")

        if blog_posts:
            context_parts.append("## 관련 블로그")
            for blog in blog_posts[:3]:
                context_parts.append(f"**{blog.title}**")
                context_parts.append(f"요약: {blog.content_summary[:200]}...")
                context_parts.append(f"URL: {blog.url}")
                context_parts.append("")

        return "\n".join(context_parts)

    def _find_related_blogs(self, context_info: Dict, question: str) -> List[Dict[str, str]]:
        related_blogs = []

        for blog_post in context_info["blog_posts"]:
            related_blogs.append(
                {
                    "title": blog_post.title,
                    "url": blog_post.url,
                    "excerpt": blog_post.excerpt[:100] + "..." if blog_post.excerpt else "",
                    "relevance": "검색 결과",
                }
            )

        for project in context_info["projects"]:
            project_blogs = BlogPost.objects.filter(related_projects=project, is_active=True).exclude(
                id__in=[b.id for b in context_info["blog_posts"]]
            )
            for blog in project_blogs[:2]:
                related_blogs.append(
                    {
                        "title": blog.title,
                        "url": blog.url,
                        "excerpt": blog.excerpt[:100] + "..." if blog.excerpt else "",
                        "relevance": f"{project.name} 관련",
                    }
                )

        return related_blogs[:5]

    def _log_conversation(
        self, user_question, processed_question, context_info, related_blogs, final_answer, response_time, session_id
    ) -> ChatLog:
        content_ids = [str(c.id) for c in context_info["company_contents"]]
        project_ids = [str(p.id) for p in context_info["projects"]]
        blog_ids = [str(b.id) for b in context_info["blog_posts"]]
        blog_links = [{"title": b["title"], "url": b["url"]} for b in related_blogs]

        chat_log = ChatLog.objects.create(
            user_question=user_question,
            processed_question=processed_question,
            retrieved_content_ids=content_ids,
            retrieved_projects=project_ids,
            retrieved_blogs=blog_ids,
            ai_response=final_answer,
            recommended_blog_links=blog_links,
            response_time_ms=int(response_time),
            session_id=session_id or "",
        )
        return chat_log

    def _get_content_hash(self, content: str) -> str:
        """컨텐츠 해시 생성 (변경 감지용)"""
        return hashlib.sha256(content.encode()).hexdigest()

    def update_single_content(self, content_id: str, content_type: str):
        """특정 컨텐츠 하나만 업데이트"""
        if content_type == "company_content":
            content = CompanyContent.objects.get(id=content_id)
            self._embed_company_content(content)
        elif content_type == "project":
            project = Project.objects.get(id=content_id)
            self._embed_project(project)
        elif content_type == "blog_post":
            blog = BlogPost.objects.get(id=content_id)
            self._embed_blog_post(blog)

    def add_custom_examples(self, question_type: str, examples: List[Dict]):
        """동적으로 새로운 예시 추가"""
        if question_type == "company":
            self.company_examples.extend(examples)
        elif question_type == "project":
            self.project_examples.extend(examples)
        elif question_type == "tech":
            self.tech_examples.extend(examples)
        elif question_type == "general":
            self.general_examples.extend(examples)

    def get_question_type_stats(self, days: int = 7) -> Dict[str, int]:
        """최근 N일간 질문 유형별 통계"""
        from datetime import timedelta

        from django.utils import timezone

        since_date = timezone.now() - timedelta(days=days)
        logs = ChatLog.objects.filter(created_at__gte=since_date)

        stats = {"company": 0, "project": 0, "tech": 0, "general": 0}

        for log in logs:
            question_type = self._analyze_question_type(log.user_question)
            stats[question_type] += 1

        return stats


# =================== 사용 예시 ===================


def example_usage():
    """동적 Few-shot 챗봇 사용 예시"""

    # 챗봇 서비스 초기화
    chatbot = CompanyChatbotService()

    # 다양한 유형의 질문 테스트
    test_questions = [
        "이 회사는 뭐하는 회사인가요?",  # company 타입
        "React 개발 가능한가요?",  # tech 타입
        "어떤 프로젝트를 진행했나요?",  # project 타입
        "견적 문의는 어떻게 하나요?",  # general 타입
    ]

    for question in test_questions:
        print(f"\n{'=' * 50}")
        print(f"질문: {question}")
        print(f"{'=' * 50}")

        result = chatbot.process_question(user_question=question, session_id="test_session_123")

        print(f"질문 유형: {result['question_type']}")
        print(f"답변:\n{result['answer']}")
        print(f"응답 시간: {result['response_time_ms']}ms")
        print(f"관련 블로그 수: {len(result['related_blogs'])}")

    return chatbot


def add_custom_examples_demo():
    """커스텀 예시 추가 데모"""

    chatbot = CompanyChatbotService()

    # 새로운 기술 관련 예시 추가
    new_tech_examples = [
        {
            "question": "AI 개발 경험이 있나요?",
            "answer": """네! AI/ML 분야에서 다양한 프로젝트 경험을 보유하고 있습니다.

🤖 **AI 개발 전문성**
- **머신러닝**: scikit-learn, pandas를 활용한 데이터 분석
- **딥러닝**: TensorFlow, PyTorch 기반 모델 개발
- **자연어처리**: LangChain, OpenAI API 연동 경험
- **컴퓨터비전**: 이미지 분류, 객체 탐지 프로젝트

🔬 **최근 AI 프로젝트**
- **챗봇 시스템**: RAG 기반 회사 전용 챗봇 개발
- **추천 엔진**: 협업 필터링 알고리즘 구현
- **감정 분석**: 고객 리뷰 자동 분석 시스템

📈 **성과**
- AI 모델 정확도 90%+ 달성
- 기존 대비 처리 속도 3배 향상""",
        }
    ]

    # 예시 추가
    chatbot.add_custom_examples("tech", new_tech_examples)

    # AI 관련 질문 테스트
    result = chatbot.process_question("머신러닝 개발 가능한가요?")
    print(result["answer"])


if __name__ == "__main__":
    # 테스트 실행
    chatbot = example_usage()

    # 질문 유형별 통계 확인
    stats = chatbot.get_question_type_stats(days=7)
    print(f"\n📊 최근 7일 질문 유형별 통계: {stats}")
