# your_app/management/commands/load_sample_data.py
# Django Management Command로 샘플 데이터 자동 생성

from datetime import date

from django.core.management.base import BaseCommand
from django.db import transaction

from app.knowledge_document.models import BlogPost, Category, CompanyContent, Project


class Command(BaseCommand):
    help = "회사 챗봇용 샘플 데이터를 자동으로 생성합니다"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="기존 데이터를 모두 삭제하고 새로 생성합니다",
        )

    def handle(self, *args, **options):
        self.stdout.write("🚀 샘플 데이터 생성을 시작합니다...")

        if options["clear"]:
            self.clear_existing_data()

        with transaction.atomic():
            # 1. 카테고리 생성
            categories = self.create_categories()
            self.stdout.write("✅ 카테고리 생성 완료")

            # 2. 회사 컨텐츠 생성
            self.create_company_contents(categories)
            self.stdout.write("✅ 회사 컨텐츠 생성 완료")

            # 3. 프로젝트 생성
            projects = self.create_projects()
            self.stdout.write("✅ 프로젝트 생성 완료")

            # 4. 블로그 포스트 생성
            self.create_blog_posts(projects)
            self.stdout.write("✅ 블로그 포스트 생성 완료")

        self.stdout.write(self.style.SUCCESS("🎉 모든 샘플 데이터 생성이 완료되었습니다!"))
        self.stdout.write("📝 다음 단계: python manage.py embed_content")

    def clear_existing_data(self):
        """기존 데이터 삭제"""
        self.stdout.write("🗑️ 기존 데이터를 삭제합니다...")
        BlogPost.objects.all().delete()
        Project.objects.all().delete()
        CompanyContent.objects.all().delete()
        Category.objects.all().delete()
        self.stdout.write("✅ 기존 데이터 삭제 완료")

    def create_categories(self):
        """카테고리 생성"""
        categories = {}

        # 최상위 카테고리들
        categories["company_info"] = Category.objects.create(
            name="회사 소개",
            category_type="company_info",
            description="회사의 기본 정보 및 소개",
            common_keywords=["회사", "기업", "소개", "정보", "개요", "회사소개"],
        )

        categories["project"] = Category.objects.create(
            name="프로젝트 포트폴리오",
            category_type="project",
            description="진행한 프로젝트들",
            common_keywords=["프로젝트", "포트폴리오", "개발", "작업", "업무", "경험"],
        )

        categories["technology"] = Category.objects.create(
            name="기술 역량",
            category_type="technology",
            description="보유한 기술 스택 및 역량",
            common_keywords=["기술", "스택", "언어", "프레임워크", "도구", "역량"],
        )

        categories["team"] = Category.objects.create(
            name="팀 구성", category_type="team", description="팀원 소개 및 구성", common_keywords=["팀", "팀원", "구성원", "직원", "멤버"]
        )

        categories["blog"] = Category.objects.create(
            name="기술 블로그",
            category_type="blog",
            description="기술 관련 블로그 포스트",
            common_keywords=["블로그", "포스트", "글", "기술글", "경험담"],
        )

        # 하위 카테고리들
        categories["vision"] = Category.objects.create(
            name="비전 및 미션",
            category_type="company_info",
            parent=categories["company_info"],
            description="회사의 비전과 미션",
            common_keywords=["비전", "미션", "목표", "가치", "철학"],
        )

        categories["frontend"] = Category.objects.create(
            name="프론트엔드",
            category_type="technology",
            parent=categories["technology"],
            description="프론트엔드 기술들",
            common_keywords=["프론트엔드", "frontend", "클라이언트", "UI", "UX"],
        )

        categories["backend"] = Category.objects.create(
            name="백엔드",
            category_type="technology",
            parent=categories["technology"],
            description="백엔드 기술들",
            common_keywords=["백엔드", "backend", "서버", "API", "데이터베이스"],
        )

        return categories

    def create_company_contents(self, categories):
        """회사 컨텐츠 생성"""

        # 1. 회사 기본 정보
        CompanyContent.objects.create(
            title="회사 기본 정보",
            content_type="company_basic",
            category=categories["company_info"],
            content="""저희 테크노베이션(TechNovation)은 2020년에 설립된 디자인 및 개발 전문 회사입니다.

**주요 사업 분야:**
- 웹사이트 및 웹앱 개발
- 모바일 앱 개발 
- UI/UX 디자인
- 브랜딩 및 그래픽 디자인
- 기술 컨설팅

**회사 위치:** 서울시 강남구 테헤란로 123번길 45, 8층
**설립일:** 2020년 3월 15일
**직원 수:** 12명 (개발자 8명, 디자이너 3명, 기획자 1명)
**대표자:** 김혁신 (CEO)

고객의 비즈니스 성공을 위한 최적의 디지털 솔루션을 제공합니다.""",
            summary="2020년 설립된 디자인 및 개발 전문 회사, 12명 규모, 웹/모바일 개발 및 디자인 서비스 제공",
            tags=["회사소개", "테크노베이션", "개발회사", "디자인", "설립", "직원"],
            search_keywords="회사 소개 정보 테크노베이션 설립 직원수 위치 대표 CEO",
            priority=5,
            is_featured=True,
        )

        # 2. 회사 비전과 미션
        CompanyContent.objects.create(
            title="회사 비전과 미션",
            content_type="company_vision",
            category=categories["vision"],
            content="""**비전 (Vision)**
기술과 창의성을 통해 더 나은 디지털 세상을 만드는 선도 기업이 되겠습니다.

**미션 (Mission)**
- 고객의 비즈니스 목표 달성을 위한 최적의 디지털 솔루션 제공
- 사용자 중심의 직관적이고 아름다운 인터페이스 설계
- 최신 기술 트렌드를 반영한 안정적이고 확장 가능한 시스템 구축
- 팀원들의 성장과 발전을 지원하는 건강한 조직문화 조성

**핵심 가치**
1. **혁신 (Innovation)**: 창의적 사고와 도전 정신
2. **품질 (Quality)**: 완벽을 추구하는 장인 정신  
3. **소통 (Communication)**: 투명하고 원활한 커뮤니케이션
4. **성장 (Growth)**: 지속적인 학습과 발전""",
            summary="기술과 창의성으로 디지털 세상을 선도하며, 혁신·품질·소통·성장의 가치 추구",
            tags=["비전", "미션", "가치", "혁신", "품질", "성장"],
            search_keywords="비전 미션 가치 목표 철학 지향점",
            priority=4,
            is_featured=True,
        )

        # 3. 프론트엔드 기술 역량
        CompanyContent.objects.create(
            title="프론트엔드 기술 역량",
            content_type="technology_stack",
            category=categories["frontend"],
            content="""저희 팀의 프론트엔드 기술 역량을 소개합니다.

**주력 기술 스택:**
- **React.js**: 5년+ 경험, 함수형 컴포넌트, Hooks, Context API 활용
- **Vue.js**: 3년+ 경험, Vue 3 Composition API, Vuex, Vue Router
- **TypeScript**: 타입 안정성을 위한 필수 도구로 활용
- **Next.js**: SSR/SSG 최적화, API Routes 활용
- **Tailwind CSS**: 효율적인 스타일링 및 반응형 디자인

**상태 관리:**
- Redux Toolkit, Zustand (React)
- Vuex, Pinia (Vue)

**개발 도구:**
- Webpack, Vite
- ESLint, Prettier
- Jest, Cypress (테스팅)

**특화 분야:**
- 반응형 웹 디자인
- 접근성 (Accessibility) 준수
- 성능 최적화 (Core Web Vitals)
- PWA (Progressive Web App) 개발""",
            summary="React, Vue 기반 프론트엔드 개발, TypeScript/Next.js 활용, 성능 최적화 전문",
            tags=["React", "Vue", "TypeScript", "Next.js", "Tailwind", "프론트엔드"],
            search_keywords="React Vue TypeScript Next.js 프론트엔드 기술 스택",
            priority=4,
        )

        # 4. 백엔드 기술 역량
        CompanyContent.objects.create(
            title="백엔드 기술 역량",
            content_type="technology_stack",
            category=categories["backend"],
            content="""안정적이고 확장 가능한 백엔드 시스템 구축 역량을 보유하고 있습니다.

**주력 기술 스택:**
- **Django REST Framework**: Python 기반 RESTful API 개발
- **FastAPI**: 고성능 비동기 API 개발
- **Node.js**: Express.js, Nest.js 프레임워크 활용
- **Spring Boot**: Java 기반 엔터프라이즈 애플리케이션

**데이터베이스:**
- **PostgreSQL**: 주력 관계형 데이터베이스
- **MySQL**: 레거시 시스템 및 일반적인 웹 프로젝트
- **MongoDB**: NoSQL 데이터베이스, 유연한 스키마 활용
- **Redis**: 캐싱 및 세션 관리

**클라우드 & 인프라:**
- AWS (EC2, RDS, S3, CloudFront)
- Docker 컨테이너화
- Nginx 웹서버 설정
- CI/CD 파이프라인 구축

**API 설계:**
- RESTful API 설계 원칙 준수
- GraphQL 활용 경험
- API 문서화 (Swagger, Postman)
- 인증/인가 (JWT, OAuth 2.0)""",
            summary="Django/FastAPI 기반 백엔드 개발, PostgreSQL/MongoDB 활용, AWS 클라우드 인프라 구축",
            tags=["Django", "FastAPI", "Node.js", "PostgreSQL", "AWS", "백엔드"],
            search_keywords="Django FastAPI Node.js 백엔드 데이터베이스 PostgreSQL",
            priority=4,
        )

        # 5. 팀원 소개
        CompanyContent.objects.create(
            title="팀원 소개",
            content_type="team_member",
            category=categories["team"],
            content="""**김혁신 (대표이사 / Full-Stack Developer)**
- 15년+ 개발 경험
- 전 네이버 개발팀 팀장
- 전문 분야: 시스템 아키텍처, 프로젝트 관리

**이창조 (CTO / Backend Lead)**
- 10년+ 백엔드 개발 경험  
- AWS Solution Architect 자격증 보유
- 전문 분야: 클라우드 인프라, API 설계

**박디자인 (Design Lead)**
- 8년+ UI/UX 디자인 경험
- 브랜딩 및 제품 디자인 전문
- Adobe Creative Suite Master

**최프론트 (Frontend Lead)**
- 7년+ 프론트엔드 개발 경험
- React/Vue 전문가
- 웹 성능 최적화 및 접근성 전문

**정풀스택 (Full-Stack Developer)**
- 5년+ 풀스택 개발 경험
- Django + React 조합 전문
- 스타트업 개발팀 출신

**한모바일 (Mobile Developer)**
- 6년+ 모바일 앱 개발 경험
- React Native, Flutter 전문
- 앱스토어 출시 경험 20+개""",
            summary="15년 경력 대표를 포함한 12명 팀, 풀스택·백엔드·프론트엔드·디자인·모바일 전문가 구성",
            tags=["팀원", "개발자", "디자이너", "경력", "전문가"],
            search_keywords="팀원 소개 개발자 디자이너 경력 전문분야",
            priority=3,
        )

        # 6. 개발 프로세스
        CompanyContent.objects.create(
            title="개발 프로세스",
            content_type="work_process",
            category=categories["company_info"],
            content="""체계적이고 효율적인 개발 프로세스로 고품질 결과물을 보장합니다.

**1. 프로젝트 시작 (1주)**
- 클라이언트 요구사항 분석 및 정리
- 기술 스택 선정 및 아키텍처 설계
- 프로젝트 일정 및 마일스톤 수립
- 와이어프레임 및 프로토타입 제작

**2. 디자인 단계 (2-3주)**
- UI/UX 디자인 컨셉 제안
- 디자인 시스템 구축
- 클라이언트 피드백 반영
- 최종 디자인 승인

**3. 개발 단계 (4-8주)**
- 애자일 방법론 적용 (2주 스프린트)
- 백엔드 API 우선 개발
- 프론트엔드 컴포넌트 개발
- 지속적 통합 및 테스트

**4. 테스트 및 배포 (1-2주)**
- 기능 테스트 및 성능 테스트
- 크로스 브라우저 호환성 검증
- 보안 검토 및 최적화
- 운영 서버 배포 및 모니터링 설정

**5. 유지보수 및 지원**
- 3개월 무상 A/S 제공
- 월별 성능 리포트 제공
- 기능 개선 및 업데이트 지원""",
            summary="요구사항 분석 → 디자인 → 애자일 개발 → 테스트 → 배포 → 유지보수의 체계적 프로세스",
            tags=["프로세스", "개발방법론", "애자일", "테스트", "배포", "유지보수"],
            search_keywords="개발 프로세스 방법론 애자일 진행과정 단계",
            priority=3,
        )

    def create_projects(self):
        """프로젝트 생성"""
        projects = []

        # 1. 글로벌 이커머스 플랫폼
        project1 = Project.objects.create(
            name="글로벌 이커머스 플랫폼",
            project_type="e_commerce",
            client_name="글로벌샵 코퍼레이션",
            description="""해외 직구 전문 이커머스 플랫폼 구축 프로젝트입니다.

**프로젝트 개요:**
다국가 배송, 다중 통화 결제, 실시간 환율 적용이 가능한 글로벌 이커머스 플랫폼을 개발했습니다.

**주요 도전과제:**
- 대용량 상품 데이터 처리 (100만+ 상품)
- 실시간 재고 관리 시스템
- 다국가 배송비 계산 로직
- 다중 결제 게이트웨이 연동

**성과:**
- 월 평균 거래액 50% 증가
- 페이지 로딩 속도 70% 개선
- 모바일 전환율 35% 향상""",
            key_features=[
                "회원가입/로그인 시스템",
                "상품 검색 및 필터링",
                "장바구니 및 위시리스트",
                "다중 결제 시스템",
                "주문 관리 시스템",
                "실시간 재고 관리",
                "다국가 배송 시스템",
                "관리자 대시보드",
                "실시간 채팅 상담",
                "리뷰 및 평점 시스템",
            ],
            technologies_used=[
                "Django REST Framework",
                "React.js",
                "PostgreSQL",
                "Redis",
                "AWS EC2/RDS/S3",
                "Docker",
                "Nginx",
                "Celery",
                "Stripe API",
                "PayPal API",
            ],
            team_size=6,
            duration_months=8.0,
            start_date=date(2023, 3, 1),
            end_date=date(2023, 10, 31),
            status="completed",
            project_url="https://globalshop-demo.com",
            is_portfolio_highlight=True,
            portfolio_image="https://example.com/portfolio/globalshop.jpg",
            search_tags=["이커머스", "쇼핑몰", "온라인몰", "글로벌", "다국가", "결제", "배송", "Django", "React", "대용량"],
        )
        projects.append(project1)

        # 2. 스마트 팩토리 관리 시스템
        project2 = Project.objects.create(
            name="스마트 팩토리 관리 시스템",
            project_type="cms",
            client_name="테크매뉴팩처링",
            description="""제조업체를 위한 종합 관리 시스템 개발 프로젝트입니다.

**프로젝트 배경:**
기존 수작업 중심의 생산 관리를 디지털화하여 효율성과 투명성을 높이는 것이 목표였습니다.

**핵심 기능:**
- 생산 계획 수립 및 관리
- 실시간 공정 모니터링
- 품질 관리 및 검사 기록
- 재고 관리 및 자재 소모 추적
- 직원 근태 및 작업 시간 관리

**기술적 특징:**
- IoT 센서 데이터 실시간 수집
- 머신러닝 기반 예측 분석
- 모바일 앱으로 현장 작업자 지원""",
            key_features=[
                "생산 계획 관리",
                "실시간 공정 모니터링",
                "품질 관리 시스템",
                "재고 및 자재 관리",
                "직원 근태 관리",
                "IoT 센서 연동",
                "데이터 분석 대시보드",
                "모바일 작업자 앱",
                "알림 및 경고 시스템",
                "보고서 자동 생성",
            ],
            technologies_used=[
                "FastAPI",
                "Vue.js",
                "PostgreSQL",
                "InfluxDB",
                "React Native",
                "MQTT",
                "Grafana",
                "Docker",
                "Kubernetes",
                "TensorFlow",
            ],
            team_size=8,
            duration_months=12.0,
            start_date=date(2022, 6, 1),
            end_date=date(2023, 5, 31),
            status="completed",
            is_portfolio_highlight=True,
            portfolio_image="https://example.com/portfolio/smartfactory.jpg",
            search_tags=["스마트팩토리", "제조", "관리시스템", "IoT", "모니터링", "FastAPI", "Vue", "머신러닝", "실시간", "대시보드"],
        )
        projects.append(project2)

        # 3. 핀테크 스타트업 모바일 앱
        project3 = Project.objects.create(
            name="핀테크 스타트업 모바일 앱",
            project_type="mobile_app",
            client_name="페이혁신",
            description="""간편 송금 및 가계부 기능을 제공하는 핀테크 모바일 앱 개발입니다.

**프로젝트 목표:**
기존 복잡한 금융 서비스를 단순화하여 누구나 쉽게 사용할 수 있는 
직관적인 모바일 금융 서비스를 제공하는 것이었습니다.

**보안 강화:**
- 생체 인증 (지문, 얼굴 인식)
- 2단계 인증
- 암호화된 통신
- 실시간 이상 거래 탐지

**사용자 경험:**
- 3초 이내 송금 완료
- 음성 인식 가계부 입력
- AI 기반 지출 분석 및 추천
- 간편한 QR 결제""",
            key_features=[
                "간편 송금 시스템",
                "QR 코드 결제",
                "가계부 및 지출 분석",
                "생체 인증",
                "실시간 알림",
                "AI 지출 패턴 분석",
                "음성 인식 입력",
                "카드 연동",
                "예산 관리",
                "금융 상품 추천",
            ],
            technologies_used=[
                "React Native",
                "Node.js",
                "Express.js",
                "MongoDB",
                "Firebase",
                "AWS Lambda",
                "TensorFlow.js",
                "WebRTC",
                "Socket.io",
                "Jest",
            ],
            team_size=5,
            duration_months=6.0,
            start_date=date(2023, 1, 15),
            end_date=date(2023, 7, 15),
            status="completed",
            project_url="https://apps.apple.com/kr/app/payinnovation",
            is_portfolio_highlight=True,
            portfolio_image="https://example.com/portfolio/fintech-app.jpg",
            search_tags=["핀테크", "모바일앱", "송금", "결제", "가계부", "React Native", "Node.js", "AI", "생체인증", "보안"],
        )
        projects.append(project3)

        # 4. 대학교 LMS 플랫폼
        project4 = Project.objects.create(
            name="대학교 LMS 플랫폼",
            project_type="web_development",
            client_name="혁신대학교",
            description="""코로나19 이후 비대면 교육 환경에 대응하기 위한 
종합 학습 관리 시스템(LMS) 구축 프로젝트입니다.

**주요 요구사항:**
- 실시간 화상 강의 지원
- 과제 제출 및 평가 시스템
- 출석 체크 및 성적 관리
- 토론 게시판 및 Q&A
- 모바일 접근성 보장

**기술적 도전:**
- 동시 접속자 5,000명 이상 지원
- 대용량 강의 영상 스트리밍
- 실시간 화상 회의 품질 보장
- 접근성 표준(WCAG) 준수""",
            key_features=[
                "실시간 화상 강의",
                "강의 녹화 및 다시보기",
                "과제 제출 시스템",
                "온라인 시험 및 퀴즈",
                "출석 관리",
                "성적 관리",
                "토론 게시판",
                "실시간 채팅",
                "파일 공유",
                "모바일 앱",
            ],
            technologies_used=[
                "Spring Boot",
                "Angular",
                "MySQL",
                "WebRTC",
                "AWS CloudFront",
                "Elasticsearch",
                "Redis",
                "Docker",
                "Jenkins",
                "Ionic",
            ],
            team_size=7,
            duration_months=10.0,
            start_date=date(2022, 1, 1),
            end_date=date(2022, 10, 31),
            status="completed",
            project_url="https://lms.innovation-univ.ac.kr",
            portfolio_image="https://example.com/portfolio/lms.jpg",
            search_tags=["LMS", "교육", "대학교", "화상강의", "이러닝", "Spring Boot", "Angular", "WebRTC", "스트리밍", "교육시스템"],
        )
        projects.append(project4)

        # 5. 부동산 중개 플랫폼
        project5 = Project.objects.create(
            name="부동산 중개 플랫폼",
            project_type="web_development",
            client_name="프롭테크 솔루션즈",
            description="""AI 기반 부동산 추천 및 중개 서비스 플랫폼 개발 프로젝트입니다.

**혁신 포인트:**
- 머신러닝 기반 매물 추천
- 가상현실(VR) 매물 투어
- 블록체인 계약 시스템
- 실시간 시세 분석

**사용자 그룹:**
- 매물 찾는 고객
- 부동산 중개업소
- 건물주/임대인""",
            key_features=[
                "AI 매물 추천",
                "VR 가상 투어",
                "실시간 매물 검색",
                "가격 비교 분석",
                "중개업소 매칭",
                "계약서 전자 서명",
                "채팅 상담",
                "매물 관리",
                "수수료 계산기",
                "시세 동향 분석",
            ],
            technologies_used=[
                "Django",
                "React",
                "PostgreSQL",
                "Elasticsearch",
                "TensorFlow",
                "Three.js",
                "WebGL",
                "AWS",
                "Celery",
                "Redis",
            ],
            team_size=6,
            duration_months=9.0,
            start_date=date(2023, 4, 1),
            end_date=date(2023, 12, 31),
            status="ongoing",
            portfolio_image="https://example.com/portfolio/proptech.jpg",
            search_tags=["부동산", "중개", "플랫폼", "AI", "VR", "Django", "React", "머신러닝", "블록체인", "프롭테크"],
        )
        projects.append(project5)

        return projects

    def create_blog_posts(self, projects):
        """블로그 포스트 생성"""

        # 프로젝트 연결을 위한 매핑
        ecommerce_project = projects[0] if projects else None
        factory_project = projects[1] if len(projects) > 1 else None
        fintech_project = projects[2] if len(projects) > 2 else None

        # 1. Django + React 이커머스 개발 경험담
        blog1 = BlogPost.objects.create(
            title="Django + React로 이커머스 플랫폼 구축하기: 실전 경험담",
            url="https://blog.technovation.co.kr/django-react-ecommerce-platform",
            excerpt="글로벌 이커머스 플랫폼 개발 과정에서 겪은 기술적 도전과제와 해결 방법을 공유합니다.",
            content_summary="""Django REST Framework와 React를 활용한 대규모 이커머스 플랫폼 개발 경험을 다룹니다.

**주요 내용:**
- Django REST Framework 프로젝트 구조 설계
- React 컴포넌트 최적화 방법
- 대용량 데이터 처리 및 페이지네이션
- 다중 결제 시스템 연동 (Stripe, PayPal)
- AWS 인프라 구축 및 배포 과정
- 성능 최적화 사례 (DB 쿼리, 프론트엔드 번들링)
- 보안 고려사항 및 대응 방법

특히 100만개 이상의 상품 데이터를 효율적으로 처리하는 방법과
실시간 재고 관리 시스템 구축 과정을 상세히 설명합니다.""",
            related_topics=["Django", "React", "이커머스", "대용량", "성능최적화", "AWS", "결제시스템", "REST API", "프로젝트후기"],
            published_date=date(2023, 11, 15),
            author="김혁신",
            is_featured=True,
            view_count=1250,
        )
        if ecommerce_project:
            blog1.related_projects.add(ecommerce_project)

        # 2. FastAPI IoT 실시간 처리
        blog2 = BlogPost.objects.create(
            title="FastAPI로 IoT 데이터 실시간 처리하기",
            url="https://blog.technovation.co.kr/fastapi-iot-realtime-processing",
            excerpt="스마트 팩토리 프로젝트에서 FastAPI를 활용한 IoT 센서 데이터 실시간 처리 시스템 구축 경험",
            content_summary="""제조업체 스마트 팩토리 관리 시스템 개발 중 FastAPI를 활용한 
IoT 센서 데이터 실시간 처리 시스템 구축 과정을 공유합니다.

**다루는 주제:**
- FastAPI vs Django 성능 비교
- 비동기 처리를 통한 대량 센서 데이터 수집
- MQTT 프로토콜을 활용한 IoT 통신
- InfluxDB를 활용한 시계열 데이터 저장
- Grafana를 통한 실시간 모니터링 대시보드
- WebSocket을 활용한 실시간 알림 시스템
- 머신러닝 모델과의 연동을 통한 예측 분석

초당 1000개 이상의 센서 데이터를 안정적으로 처리하는
아키텍처 설계와 최적화 방법을 설명합니다.""",
            related_topics=[
                "FastAPI",
                "IoT",
                "실시간처리",
                "비동기",
                "MQTT",
                "InfluxDB",
                "Grafana",
                "스마트팩토리",
                "센서데이터",
                "WebSocket",
            ],
            published_date=date(2023, 9, 20),
            author="이창조",
            is_featured=True,
            view_count=890,
        )
        if factory_project:
            blog2.related_projects.add(factory_project)

        # 3. React Native 금융앱 보안
        blog3 = BlogPost.objects.create(
            title="React Native로 금융 앱 개발시 보안 고려사항",
            url="https://blog.technovation.co.kr/react-native-fintech-security",
            excerpt="핀테크 모바일 앱 개발 과정에서 적용한 보안 강화 방법과 모범 사례를 소개합니다.",
            content_summary="""핀테크 스타트업 모바일 앱 개발 프로젝트를 통해 학습한
React Native 기반 금융 앱의 보안 강화 방법을 정리했습니다.

**보안 강화 방법:**
- 생체 인증 (TouchID, FaceID) 구현
- 앱 변조 및 루팅 탐지
- 암호화 통신 및 인증서 피닝
- 민감 데이터 안전한 저장 방법
- 2단계 인증 시스템 구축
- 실시간 이상 거래 탐지 로직
- 코드 난독화 및 앱 보호

금융권 보안 요구사항을 만족하면서도 사용자 경험을 
해치지 않는 균형점을 찾는 과정을 공유합니다.""",
            related_topics=["React Native", "핀테크", "모바일보안", "생체인증", "암호화", "금융앱", "보안", "2단계인증", "코드난독화", "앱보호"],
            published_date=date(2023, 8, 10),
            author="한모바일",
            is_featured=True,
            view_count=675,
        )
        if fintech_project:
            blog3.related_projects.add(fintech_project)

        # 4. Vue.js 3 Composition API 마이그레이션
        BlogPost.objects.create(
            title="Vue.js 3 Composition API 마이그레이션 가이드",
            url="https://blog.technovation.co.kr/vue3-composition-api-migration",
            excerpt="Vue.js 2에서 3로 마이그레이션하면서 Composition API를 도입한 경험과 팁을 공유합니다.",
            content_summary="""스마트 팩토리 관리 시스템의 프론트엔드를 Vue.js 2에서 3로 
마이그레이션하면서 Composition API를 도입한 실전 경험을 다룹니다.

**마이그레이션 과정:**
- Vue 2 Options API vs Vue 3 Composition API 비교
- 점진적 마이그레이션 전략 수립
- TypeScript 도입 및 타입 안정성 확보
- Pinia를 활용한 상태 관리 개선
- 성능 향상 사례 (Bundle 크기 감소, 렌더링 최적화)
- 기존 컴포넌트 재사용 방법
- 테스트 코드 마이그레이션

대규모 Vue.js 프로젝트의 마이그레이션 시 고려해야 할
사항들과 주의점을 실제 사례를 통해 설명합니다.""",
            related_topics=[
                "Vue.js",
                "Composition API",
                "마이그레이션",
                "TypeScript",
                "Pinia",
                "성능최적화",
                "프론트엔드",
                "리팩토링",
                "상태관리",
            ],
            published_date=date(2023, 7, 5),
            author="최프론트",
            view_count=445,
        )

        # 5. AWS 비용 최적화
        BlogPost.objects.create(
            title="AWS 비용 최적화를 위한 인프라 설계 전략",
            url="https://blog.technovation.co.kr/aws-cost-optimization-strategy",
            excerpt="클라우드 비용을 50% 절감한 AWS 인프라 최적화 경험과 구체적인 방법들을 소개합니다.",
            content_summary="""여러 프로젝트의 AWS 인프라 운영 경험을 바탕으로
비용 최적화를 위한 실전 전략을 정리했습니다.

**비용 최적화 방법:**
- EC2 인스턴스 타입 최적화 및 Reserved Instance 활용
- Auto Scaling을 통한 탄력적 리소스 관리
- S3 스토리지 클래스 최적화 (Standard, IA, Glacier)
- CloudFront CDN 활용한 트래픽 비용 절감
- RDS 최적화 (Read Replica, 백업 정책)
- 모니터링 및 알림 시스템 구축
- 태그 기반 리소스 관리

실제 프로젝트에서 월 $3,000에서 $1,500로 비용을 
50% 절감한 구체적인 사례와 방법을 공유합니다.""",
            related_topics=["AWS", "비용최적화", "클라우드", "EC2", "S3", "CloudFront", "Auto Scaling", "인프라", "모니터링"],
            published_date=date(2023, 6, 15),
            author="이창조",
            view_count=320,
        )

        # 6. 디자인 시스템 구축
        BlogPost.objects.create(
            title="UI/UX 디자인 시스템 구축하기: Figma에서 코드까지",
            url="https://blog.technovation.co.kr/design-system-figma-to-code",
            excerpt="일관된 사용자 경험을 위한 디자인 시스템 구축 과정과 개발팀과의 협업 방법을 소개합니다.",
            content_summary="""여러 프로젝트를 진행하면서 구축한 디자인 시스템의
설계 과정과 개발팀과의 효율적인 협업 방법을 공유합니다.

**디자인 시스템 구성 요소:**
- 컬러 팔레트 및 타이포그래피 시스템
- 컴포넌트 라이브러리 구축 (Atomic Design)
- 아이콘 시스템 및 일러스트레이션 가이드
- 반응형 그리드 시스템
- 애니메이션 및 인터랙션 가이드라인

**개발팀과의 협업:**
- Figma에서 Storybook으로의 전환 과정
- 디자인 토큰을 활용한 일관성 유지
- 컴포넌트 버전 관리 및 업데이트 전략
- 접근성 가이드라인 적용

디자인과 개발 간의 간극을 줄이고 일관된 사용자 
경험을 제공하기 위한 실전 노하우를 다룹니다.""",
            related_topics=["디자인시스템", "UI/UX", "Figma", "Storybook", "컴포넌트", "디자인토큰", "접근성", "협업", "Atomic Design"],
            published_date=date(2023, 5, 20),
            author="박디자인",
            view_count=280,
        )
