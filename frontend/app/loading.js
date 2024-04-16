/**
 * Loading component.
 *
 * @returns {JSX.Element} - The rendered JSX element.
 */
export default function Loading() {
    /**
     * Renders a spinning circle to indicate loading.
     */
    return (
        <div className="flex items-center justify-center h-screen">
            <div className="animate-spin rounded-full h-32 w-32 border-t-2 border-b-2 border-white"></div>
        </div>
    )
}