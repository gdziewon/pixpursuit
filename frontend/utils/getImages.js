export async function getImages({ limit, page, query, sort, searchMode }) {
  try {
    const response = await fetch(
      `/api/getImages?limit=${limit}&page=${page}&query=${encodeURIComponent(
        query
      )}&sort=${sort}&searchMode=${searchMode}`
    );

    if (!response.ok) {
      const errorData = await response.json();
      console.error(
        `Failed to fetch images: ${response.statusText}`,
        errorData
      );
      throw new Error(`Failed to fetch images: ${response.statusText}`);
    }
    const images = await response.json();
    return images;
  } catch (error) {
    console.error(`Error occurred while fetching images: ${error.message}`);
    throw error;
  }
}
