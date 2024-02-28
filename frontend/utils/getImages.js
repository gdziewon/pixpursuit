export async function getImages({ limit, page, query, sort }) {
  try {
    const response = await fetch(`/api/getImages?limit=${limit}&page=${page}&query=${query}&sort=${sort}`);

    if (!response.ok) {
      throw new Error(`Failed to fetch images: ${response.statusText}`);
    }
    const images = await response.json();
    return images;
  } catch (error) {
    console.error(`Error occurred while fetching images: ${error.message}`);
    throw error;
  }
}