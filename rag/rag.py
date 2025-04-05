from google.cloud import storage
from google.oauth2 import service_account
from vertexai.preview import rag
from vertexai.generative_models import GenerativeModel, Tool
import vertexai

PROJECT_ID = "pw-techfest-team-05"
credentials = service_account.Credentials.from_service_account_file(
    "pw-techfest-team-05-9aa12c8e1165.json"
)

def upload_file_to_gcs(uploaded_file, bucket_name="rag-techfest"):
    client = storage.Client(credentials=credentials, project=PROJECT_ID)
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(f"uploads/{uploaded_file.name}")

    blob.upload_from_file(uploaded_file, content_type=uploaded_file.content_type)
    return f"gs://{bucket.name}/{blob.name}"


def do(file_path):
    # Create a RAG Corpus, Import Files, and Generate a response

    display_name = "test_corpus"
    # paths = ["gs://my_bucket/my_files_dir"]  # Supports Google Cloud Storage and Google Drive Links

    # Initialize Vertex AI API once per session
    vertexai.init(project=PROJECT_ID, location="us-central1", credentials=credentials)

    # Create RagCorpus
    # Configure embedding model, for example "text-embedding-005".
    embedding_model_config = rag.RagEmbeddingModelConfig(
        vertex_prediction_endpoint=rag.VertexPredictionEndpoint(
            publisher_model="publishers/google/models/text-embedding-005"
        )
    )

    rag_corpus = rag.create_corpus(
        display_name=display_name,
        backend_config=rag.RagVectorDbConfig(
            rag_embedding_model_config=embedding_model_config
        ),
    )

    # Import Files to the RagCorpus
    rag.import_files(
        rag_corpus.name,
        [file_path],
        # Optional
        transformation_config=rag.TransformationConfig(
            chunking_config=rag.ChunkingConfig(
                chunk_size=512,
                chunk_overlap=100,
            ),
        ),
        max_embedding_requests_per_min=1000,  # Optional
    )

    # Direct context retrieval
    rag_retrieval_config = rag.RagRetrievalConfig(
        top_k=3,  # Optional
        filter=rag.Filter(vector_distance_threshold=0.5),  # Optional
    )
    response = rag.retrieval_query(
        rag_resources=[
            rag.RagResource(
                rag_corpus=rag_corpus.name,
                # Optional: supply IDs from `rag.list_files()`.
                # rag_file_ids=["rag-file-1", "rag-file-2", ...],
            )
        ],
        text="What is git and why it is helpful?",
        rag_retrieval_config=rag_retrieval_config,
    )
    print(response)

    # Enhance generation
    # Create a RAG retrieval tool
    rag_retrieval_tool = Tool.from_retrieval(
        retrieval=rag.Retrieval(
            source=rag.VertexRagStore(
                rag_resources=[
                    rag.RagResource(
                        rag_corpus=rag_corpus.name,  # Currently only 1 corpus is allowed.
                        # Optional: supply IDs from `rag.list_files()`.
                        # rag_file_ids=["rag-file-1", "rag-file-2", ...],
                    )
                ],
                rag_retrieval_config=rag_retrieval_config,
            ),
        )
    )

    # Create a Gemini model instance
    rag_model = GenerativeModel(
        model_name="gemini-2.0-flash-001", tools=[rag_retrieval_tool]
    )

    # Generate response
    response = rag_model.generate_content("What is RAG and why it is helpful?")
    print(response.text)
