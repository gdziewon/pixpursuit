/**
 * Fetches images from the server.
 *
 * @param {Object} params - The parameters for the fetch request.
 * @param {number} params.limit - The maximum number of images to fetch.
 * @param {number} params.page - The page number to fetch.
 * @param {string} params.query - The query string to use for the fetch request.
 * @param {string} params.sort - The sort order for the fetch request.
 * @param {string} params.searchMode - The search mode for the fetch request.
 * @returns {Promise<Array<Object>>} - A promise that resolves to an array of image objects.
 * @throws {Error} - If the fetch request fails.
 */
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
