import os
import time
from pathlib import Path
from dotenv import load_dotenv
from tqdm.auto import tqdm
from pinecone import Pinecone, ServerlessSpec
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = "us-east-1"
PINECONE_INDEX_NAME = "rag-ai-laywer"

os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

UPLOAD_DIR = "./uploaded_docs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize Pinecone instance
pc = Pinecone(api_key=PINECONE_API_KEY)
spec = ServerlessSpec(cloud="aws", region=PINECONE_ENV)
existing_index = [i["name"] for i in pc.list_indexes()]

if PINECONE_INDEX_NAME not in existing_index:
    pc.create_index(
        name=PINECONE_INDEX_NAME,
        dimension=768, # Dimension of Google Embedding
        metric="dotproduct",
        spec=spec
    )
    while not pc.describe_index(PINECONE_INDEX_NAME).status["ready"]:
        time.sleep(1)

index = pc.Index(PINECONE_INDEX_NAME)

def load_vectorstore(uploaded_files):
    """
    Process uploaded PDF files and store them in Pinecone vectorstore
    """
    try:
        embedding_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        file_paths = []
        
        # Validate input
        if not uploaded_files:
            print("❌ No files provided")
            return
        
        print(f"📄 Processing {len(uploaded_files)} files...")
        
        # 1) Save uploaded files
        for file in uploaded_files:
            if not file.filename or file.filename == "":
                print(f"⚠️ Skipping file with empty filename")
                continue
                
            if not file.filename.lower().endswith('.pdf'):
                print(f"⚠️ Skipping non-PDF file: {file.filename}")
                continue
            
            save_path = Path(UPLOAD_DIR) / file.filename
            
            # Reset file pointer to beginning
            file.file.seek(0)
            
            # Save file
            try:
                with open(save_path, "wb") as f:
                    content = file.file.read()
                    if len(content) == 0:
                        print(f"⚠️ File {file.filename} is empty")
                        continue
                    f.write(content)
                    
                file_paths.append(str(save_path))
                print(f"✅ Saved {file.filename} ({len(content)} bytes)")
                
            except Exception as e:
                print(f"❌ Error saving {file.filename}: {str(e)}")
                continue
        
        if not file_paths:
            print("❌ No valid PDF files to process")
            return
        
        # Collect all chunks from all files
        all_texts = []
        all_metadatas = []
        all_ids = []
        
        # 2) Process each file
        for file_path in file_paths:
            try:
                print(f"📖 Loading {os.path.basename(file_path)}...")
                
                loader = PyPDFLoader(file_path)
                documents = loader.load()
                
                if not documents:
                    print(f"⚠️ No content extracted from {file_path}")
                    continue
                
                print(f"📄 Loaded {len(documents)} pages from {os.path.basename(file_path)}")
                
                # Split documents into chunks
                splitter = RecursiveCharacterTextSplitter(
                    chunk_size=500,
                    chunk_overlap=100
                )
                chunks = splitter.split_documents(documents)
                
                if not chunks:
                    print(f"⚠️ No chunks created from {file_path}")
                    continue
                
                print(f"✂️ Created {len(chunks)} chunks from {os.path.basename(file_path)}")
                
                # Extract text and metadata
                texts = [chunk.page_content for chunk in chunks]
                metadatas = [chunk.metadata for chunk in chunks]
                ids = [f"{Path(file_path).stem}-{i}" for i in range(len(chunks))]
                
                # Filter out empty chunks
                non_empty_data = [(t, m, i) for t, m, i in zip(texts, metadatas, ids) if t.strip()]
                
                if non_empty_data:
                    texts, metadatas, ids = zip(*non_empty_data)
                    all_texts.extend(texts)
                    all_metadatas.extend(metadatas)
                    all_ids.extend(ids)
                    print(f"✅ Added {len(texts)} non-empty chunks from {os.path.basename(file_path)}")
                else:
                    print(f"⚠️ All chunks were empty for {file_path}")
                
            except Exception as e:
                print(f"❌ Error processing {file_path}: {str(e)}")
                continue
        
        if not all_texts:
            print("❌ No text chunks to process. Check your PDF files.")
            return
        
        # 3) Generate embeddings for all chunks
        print(f"🔍 Embedding {len(all_texts)} chunks...")
        try:
            embeddings = embedding_model.embed_documents(all_texts)
            print(f"✅ Generated {len(embeddings)} embeddings")
        except Exception as e:
            print(f"❌ Error generating embeddings: {str(e)}")
            return
        
        # 4) Prepare vectors for Pinecone (correct format)
        vectors = []
        for i, (text, embedding, metadata, doc_id) in enumerate(zip(all_texts, embeddings, all_metadatas, all_ids)):
            # Add the original text to metadata for easy retrieval
            metadata['text'] = text
            
            vector = {
                "id": doc_id,
                "values": embedding,
                "metadata": metadata
            }
            vectors.append(vector)
        
        if not vectors:
            print("❌ No vectors created")
            return
        
        # 5) Upsert to Pinecone in batches
        print(f"📤 Uploading {len(vectors)} vectors to Pinecone...")
        batch_size = 100  # Pinecone recommended batch size
        
        try:
            with tqdm(total=len(vectors), desc="Upserting to Pinecone") as progress:
                for i in range(0, len(vectors), batch_size):
                    batch = vectors[i:i + batch_size]
                    
                    try:
                        index.upsert(vectors=batch)
                        progress.update(len(batch))
                    except Exception as e:
                        print(f"❌ Error upserting batch {i//batch_size + 1}: {str(e)}")
                        raise
            
            print(f"✅ Successfully uploaded {len(vectors)} vectors to Pinecone")
            
            # Verify upload
            stats = index.describe_index_stats()
            print(f"📊 Index now contains {stats.total_vector_count} total vectors")
            
        except Exception as e:
            print(f"❌ Error during Pinecone upload: {str(e)}")
            raise
        
        # 6) Cleanup uploaded files (optional)
        for file_path in file_paths:
            try:
                os.remove(file_path)
                print(f"🗑️ Cleaned up {os.path.basename(file_path)}")
            except Exception as e:
                print(f"⚠️ Could not remove {file_path}: {str(e)}")
                
    except Exception as e:
        print(f"❌ Critical error in load_vectorstore: {str(e)}")
        raise