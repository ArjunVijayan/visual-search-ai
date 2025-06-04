import pickle
import dotenv
import uuid
import os

dotenv.load_dotenv()
pickle_dir = os.getenv('PICKLE_STORAGE_PATH')

def pickle_vector_store(vector_store, is_image=False):
    """
    Pickles the vector store to a file in the specified directory.
    Args:
        vector_store: The vector store to pickle.
        is_image (bool): If True, saves in the image directory; otherwise, saves in the document directory.
    Returns:
        str: The file path where the vector store is saved.
    """

    file_name = f'vector_store_image_{uuid.uuid4()}.pkl' if is_image else f'vector_store_{uuid.uuid4()}.pkl'

    file_path = os.path.join(pickle_dir, file_name)
    with open(file_path, 'wb') as f:
        pickle.dump(vector_store, f)
    print(f"Vector store saved to {file_path}")

    return file_path

def unpickle_vector_store(file_path):
    """
    Unpickles the vector store from a file in the specified directory.
    Args:
        is_image (bool): If True, loads from the image directory; otherwise, loads from the document directory.
    Returns:
        The unpickled vector store.
    """
    with open(file_path, 'rb') as f:
        vector_store = pickle.load(f)
    print(f"Vector store loaded from {file_path}")

    return vector_store
