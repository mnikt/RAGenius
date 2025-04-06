from google.cloud import storage
from google.oauth2 import service_account
from vertexai.preview import rag
from vertexai.generative_models import GenerativeModel, Tool
import vertexai


PROJECT_ID = "pw-techfest-team-05"
credentials = service_account.Credentials.from_service_account_file(
    "pw-techfest-team-05-9aa12c8e1165.json"
)
# Initialize Vertex AI API once per session
vertexai.init(project=PROJECT_ID, location="us-central1", credentials=credentials)


def upload_file(uploaded_file, file, path):
    url = upload_file_to_gcs(uploaded_file, file.id)
    upload_file_to_rag(url, file.directory.corpus, path)


def upload_file_to_gcs(uploaded_file, file_id, bucket_name="rag-techfest") -> str:
    client = storage.Client(credentials=credentials, project=PROJECT_ID)
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(f"{file_id}.pdf")

    blob.upload_from_file(uploaded_file, content_type=uploaded_file.content_type)
    return f"gs://{bucket.name}/{blob.name}"


def upload_file_to_rag(uploaded_file_gs_url, corpus_name, path):
    rag.import_files(
        corpus_name=corpus_name,
        paths=[uploaded_file_gs_url],
        transformation_config=rag.TransformationConfig(
            rag.ChunkingConfig(chunk_size=512, chunk_overlap=100)
        ),
        max_embedding_requests_per_min=900,  # Optional
    )

def delete_file(file, bucket_name="rag-techfest"):
    client = storage.Client(credentials=credentials, project=PROJECT_ID)
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(f"uploads/{file.id}.pdf")
    blob.delete()


def create_corpus(display_name):
    embedding_model_config = rag.RagEmbeddingModelConfig(
        vertex_prediction_endpoint=rag.VertexPredictionEndpoint(
            publisher_model="publishers/google/models/text-embedding-005"
        )
    )

    return rag.create_corpus(
        display_name=display_name,
        backend_config=rag.RagVectorDbConfig(
            rag_embedding_model_config=embedding_model_config
        ),
    ).name


def delete_corpus(display_name):
    rag.delete_corpus(display_name)


def ask_question(question: str, corpus_name: str) -> str:
    rag_retrieval_config = rag.RagRetrievalConfig(
        filter=rag.Filter(vector_distance_threshold=0.5),  # Optional
    )

    response = rag.retrieval_query(
        rag_resources=[
            rag.RagResource(
                rag_corpus=corpus_name
            )
        ],
        text=question,
        rag_retrieval_config=rag_retrieval_config,
    )
    contexts = response.contexts.contexts
    if len(contexts) > 0:
        return contexts[0].text
    return "I cannot answer this question"


def do(file_path):
    # Create a RAG Corpus, Import Files, and Generate a response

    display_name = "test_corpus"
    # paths = ["gs://my_bucket/my_files_dir"]  # Supports Google Cloud Storage and Google Drive Links

    # Create RagCorpus
    # Configure embedding model, for example "text-embedding-005".

    # Import Files to the RagCorpus

    # Direct context retrieval


    # Enhance generation
    # Create a RAG retrieval tool
    # rag_retrieval_tool = Tool.from_retrieval(
    #     retrieval=rag.Retrieval(
    #         source=rag.VertexRagStore(
    #             rag_resources=[
    #                 rag.RagResource(
    #                     rag_corpus=rag_corpus.name,  # Currently only 1 corpus is allowed.
    #                     # Optional: supply IDs from `rag.list_files()`.
    #                     # rag_file_ids=["rag-file-1", "rag-file-2", ...],
    #                 )
    #             ],
    #             rag_retrieval_config=rag_retrieval_config,
    #         ),
    #     )
    # )
    #
    # # Create a Gemini model instance
    # rag_model = GenerativeModel(
    #     model_name="gemini-2.0-flash-001", tools=[rag_retrieval_tool]
    # )
    #
    # # Generate response
    # response = rag_model.generate_content("What is RAG and why it is helpful?")
    # print(response.text)
