import uuid

from django.core.validators import URLValidator
from django.db import models

# =================== 1. 카테고리 시스템 ===================


class Category(models.Model):
    """컨텐츠 카테고리 - 간단한 계층 구조"""

    CATEGORY_TYPES = [
        ("company_info", "회사 정보"),
        ("project", "프로젝트"),
        ("technology", "기술 스택"),
        ("team", "팀 구성"),
        ("service", "제공 서비스"),
        ("process", "업무 프로세스"),
        ("blog", "블로그"),
        ("etc", "기타"),
    ]

    name = models.CharField(max_length=100, verbose_name="카테고리명")
    category_type = models.CharField(max_length=20, choices=CATEGORY_TYPES, verbose_name="카테고리 유형")
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE, verbose_name="상위 카테고리")
    description = models.TextField(blank=True, verbose_name="설명")

    # 검색 최적화용
    common_keywords = models.JSONField(
        default=list, verbose_name="관련 키워드", help_text="이 카테고리와 관련된 키워드들 (예: ['React', '프론트엔드', 'UI'])"
    )

    is_active = models.BooleanField(default=True, verbose_name="활성 상태")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "카테고리"
        verbose_name_plural = "카테고리"
        ordering = ["category_type", "name"]

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name


# =================== 2. 핵심 컨텐츠 모델 ===================


class CompanyContent(models.Model):
    """회사 관련 모든 컨텐츠를 저장하는 핵심 모델"""

    CONTENT_TYPES = [
        ("company_basic", "회사 기본정보"),
        ("company_vision", "비전/미션"),
        ("company_history", "회사 연혁"),
        ("team_member", "팀원 소개"),
        ("project_portfolio", "프로젝트 포트폴리오"),
        ("technology_stack", "기술 스택"),
        ("service_offering", "제공 서비스"),
        ("work_process", "업무 프로세스"),
        ("client_testimonial", "고객 후기"),
        ("blog_content", "블로그 내용"),
        ("faq", "자주 묻는 질문"),
    ]

    PRIORITY_LEVELS = [
        (1, "낮음"),
        (2, "보통"),
        (3, "높음"),
        (4, "매우 높음"),
        (5, "최우선"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    title = models.CharField(max_length=300, verbose_name="제목")
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES, verbose_name="컨텐츠 유형")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="카테고리")

    # 핵심 내용
    content = models.TextField(verbose_name="내용", help_text="이 내용이 AI 챗봇의 답변 소스가 됩니다.")
    summary = models.TextField(blank=True, verbose_name="요약", help_text="간단한 요약 (선택사항)")

    # 검색 최적화
    tags = models.JSONField(default=list, verbose_name="태그", help_text="검색 키워드 (예: ['React', 'e-commerce', '쇼핑몰'])")
    search_keywords = models.TextField(blank=True, verbose_name="추가 검색 키워드", help_text="사용자가 다양한 방식으로 질문할 수 있는 키워드들")

    # 우선순위 및 상태
    priority = models.IntegerField(
        choices=PRIORITY_LEVELS, default=2, verbose_name="우선순위", help_text="높을수록 검색 결과에서 우선 표시"
    )
    is_active = models.BooleanField(default=True, verbose_name="활성 상태")
    is_featured = models.BooleanField(default=False, verbose_name="주요 컨텐츠", help_text="중요한 회사 정보인 경우 체크")

    # 추적 정보
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "회사 컨텐츠"
        verbose_name_plural = "회사 컨텐츠"
        ordering = ["-priority", "-updated_at"]
        indexes = [
            models.Index(fields=["content_type", "is_active"]),
            models.Index(fields=["priority", "is_featured"]),
        ]

    def __str__(self):
        return f"[{self.get_content_type_display()}] {self.title}"


# =================== 3. 프로젝트 전용 모델 ===================


class Project(models.Model):
    """프로젝트 상세 정보 - 포트폴리오 질문에 특화"""

    PROJECT_STATUS = [
        ("completed", "완료"),
        ("ongoing", "진행중"),
        ("paused", "일시중단"),
        ("cancelled", "취소"),
    ]

    PROJECT_TYPES = [
        ("web_development", "웹 개발"),
        ("mobile_app", "모바일 앱"),
        ("e_commerce", "이커머스"),
        ("cms", "CMS/관리시스템"),
        ("portfolio", "포트폴리오 사이트"),
        ("corporate", "기업 사이트"),
        ("landing_page", "랜딩 페이지"),
        ("api_development", "API 개발"),
        ("ui_ux_design", "UI/UX 디자인"),
        ("consulting", "컨설팅"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=200, verbose_name="프로젝트명")
    project_type = models.CharField(max_length=20, choices=PROJECT_TYPES, verbose_name="프로젝트 유형")
    client_name = models.CharField(max_length=100, blank=True, verbose_name="클라이언트명")

    # 프로젝트 상세 정보
    description = models.TextField(verbose_name="프로젝트 설명")
    key_features = models.JSONField(default=list, verbose_name="주요 기능", help_text="['회원가입/로그인', '결제시스템', '관리자 페이지']")
    technologies_used = models.JSONField(
        default=list, verbose_name="사용 기술", help_text="['Django', 'React', 'PostgreSQL']"
    )

    # 프로젝트 메타 정보
    team_size = models.IntegerField(null=True, blank=True, verbose_name="팀 크기")
    duration_months = models.FloatField(null=True, blank=True, verbose_name="개발 기간(개월)")
    start_date = models.DateField(null=True, blank=True, verbose_name="시작일")
    end_date = models.DateField(null=True, blank=True, verbose_name="종료일")

    # 상태 및 링크
    status = models.CharField(max_length=10, choices=PROJECT_STATUS, default="completed")
    project_url = models.URLField(blank=True, verbose_name="프로젝트 URL")
    github_url = models.URLField(blank=True, verbose_name="GitHub URL")

    # 포트폴리오 표시용
    is_portfolio_highlight = models.BooleanField(default=False, verbose_name="포트폴리오 대표 프로젝트")
    portfolio_image = models.URLField(blank=True, verbose_name="포트폴리오 이미지 URL")

    # 검색 최적화
    search_tags = models.JSONField(default=list, verbose_name="검색 태그", help_text="이 프로젝트와 관련된 모든 키워드")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "프로젝트"
        verbose_name_plural = "프로젝트"
        ordering = ["-is_portfolio_highlight", "-end_date"]

    def __str__(self):
        return f"{self.name} ({self.get_project_type_display()})"


# =================== 4. 블로그 연동 모델 ===================


class BlogPost(models.Model):
    """블로그 포스트 정보 - 답변에 관련 블로그 링크 포함"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    title = models.CharField(max_length=300, verbose_name="블로그 제목")
    url = models.URLField(unique=True, max_length=500, verbose_name="블로그 URL")

    # 블로그 내용 (검색용)
    excerpt = models.TextField(blank=True, verbose_name="발췌/요약", help_text="블로그의 핵심 내용 요약")
    content_summary = models.TextField(blank=True, verbose_name="내용 요약", help_text="AI가 검색할 수 있도록 블로그 내용을 요약")

    # 관련성 태그
    related_topics = models.JSONField(
        default=list, verbose_name="관련 주제", help_text="['React', 'Django', 'API개발', '프로젝트후기']"
    )
    related_projects = models.ManyToManyField(Project, blank=True, verbose_name="관련 프로젝트")

    # 메타 정보
    published_date = models.DateField(null=True, blank=True, verbose_name="발행일")
    author = models.CharField(max_length=100, blank=True, verbose_name="작성자")

    # 추천 우선순위
    is_featured = models.BooleanField(default=False, verbose_name="추천 포스트")
    view_count = models.IntegerField(default=0, verbose_name="조회수")

    is_active = models.BooleanField(default=True, verbose_name="활성 상태")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "블로그 포스트"
        verbose_name_plural = "블로그 포스트"
        ordering = ["-is_featured", "-published_date"]

    def __str__(self):
        return self.title


# =================== 5. 크로마 벡터 연동 ===================


class ChromaVector(models.Model):
    """크로마 벡터 저장소와의 연동 정보"""

    CONTENT_SOURCE_TYPES = [
        ("company_content", "회사 컨텐츠"),
        ("project", "프로젝트"),
        ("blog_post", "블로그 포스트"),
    ]

    # 어떤 컨텐츠의 벡터인지 식별
    content_type = models.CharField(max_length=20, choices=CONTENT_SOURCE_TYPES)
    content_id = models.UUIDField(verbose_name="원본 컨텐츠 ID")

    # 크로마 정보
    vector_id = models.CharField(max_length=200, unique=True, verbose_name="크로마 벡터 ID")
    collection_name = models.CharField(max_length=100, default="company_knowledge", verbose_name="컬렉션명")

    # 임베딩 설정
    embedding_model = models.CharField(max_length=100, default="text-embedding-3-small", verbose_name="임베딩 모델")
    last_embedded_at = models.DateTimeField(auto_now=True, verbose_name="마지막 임베딩 시간")

    # 성능 추적
    retrieval_count = models.IntegerField(default=0, verbose_name="검색된 횟수")
    avg_relevance_score = models.FloatField(null=True, blank=True, verbose_name="평균 관련성 점수")

    # 업데이트 관리
    needs_update = models.BooleanField(default=False, verbose_name="업데이트 필요")
    source_content_hash = models.CharField(max_length=64, blank=True, verbose_name="원본 내용 해시")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "크로마 벡터"
        verbose_name_plural = "크로마 벡터"
        unique_together = ["content_type", "content_id"]
        indexes = [
            models.Index(fields=["content_type", "needs_update"]),
        ]

    def __str__(self):
        return f"{self.get_content_type_display()} - {self.vector_id[:20]}..."


# =================== 6. 질의응답 로그 ===================


class ChatLog(models.Model):
    """사용자 질문과 AI 답변 로그"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    # 질문 정보
    user_question = models.TextField(verbose_name="사용자 질문")
    processed_question = models.TextField(blank=True, verbose_name="처리된 질문")

    # 검색 결과
    retrieved_content_ids = models.JSONField(default=list, verbose_name="검색된 컨텐츠 ID들")
    retrieved_projects = models.JSONField(default=list, verbose_name="검색된 프로젝트 ID들")
    retrieved_blogs = models.JSONField(default=list, verbose_name="검색된 블로그 ID들")

    # AI 답변
    ai_response = models.TextField(verbose_name="AI 답변")
    recommended_blog_links = models.JSONField(default=list, verbose_name="추천된 블로그 링크들")

    # 성능 지표
    response_time_ms = models.IntegerField(null=True, blank=True, verbose_name="응답 시간(ms)")

    # 사용자 피드백
    user_rating = models.IntegerField(
        null=True,
        blank=True,
        choices=[(1, "매우 나쁨"), (2, "나쁨"), (3, "보통"), (4, "좋음"), (5, "매우 좋음")],
        verbose_name="사용자 평가",
    )
    user_feedback = models.TextField(blank=True, verbose_name="사용자 피드백")

    # 세션 추적
    session_id = models.CharField(max_length=100, blank=True, verbose_name="세션 ID")

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "채팅 로그"
        verbose_name_plural = "채팅 로그"
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.user_question[:50]}... ({self.timestamp.strftime('%Y-%m-%d %H:%M')})"
