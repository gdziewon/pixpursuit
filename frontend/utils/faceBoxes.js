import axios from "axios";
import Image from "next/image";
import { useState, useEffect, useRef } from "react";
import { HeartIcon } from "@heroicons/react/24/solid";
import '@/styles/design_styles.css';
import SuccessWindow from '@/utils/SuccessWindow';
import ErrorWindow from '@/utils/ErrorWindow';
import { MagnifyingGlassIcon } from "@heroicons/react/24/solid";

/**
 * Renders a box overlay for an image with various interactive features.
 *
 * @param {Object} props - The props.
 * @param {Object} props.image - The image object.
 * @param {Array<Array<number>>} props.boxes - The boxes to overlay on the image.
 * @param {Object} props.originalSize - The original size of the image.
 * @param {Object} props.session - The session object.
 * @param {boolean} props.showHeartOverlay - Whether to show a heart overlay.
 * @returns {JSX.Element} - The rendered JSX element.
 */
export function BoxOverlay({ image, boxes, originalSize, session, showHeartOverlay }) {
    const displayWidth = 800;  // Adjust as needed
    const displayHeight = 800; // Adjust as needed

    const [editableBoxIndex, setEditableBoxIndex] = useState(null);
    const [boxText, setBoxText] = useState('');
    const [isMouseOver, setIsMouseOver] = useState(false);
    const isLoggedIn = session && session.accessToken;

    const overlayRef = useRef(null); // Ref for the BoxOverlay component itself
    const [scaleX, setScaleX] = useState(1);
    const [errorMessage, setErrorMessage] = useState(null);
    const [successMessage, setSuccessMessage] = useState(null);
    const [isPlusClicked, setIsPlusClicked] = useState(false);
    const [enlargedImage, setEnlargedImage] = useState(null);

    useEffect(() => {
        const updateScale = () => {
            if (overlayRef.current) {
                // Assuming the BoxOverlay component's width matches its container's width
                const width = overlayRef.current.offsetWidth;
                const newScaleX = width / originalSize.width;
                setScaleX(newScaleX);
            }
        };

        updateScale(); // Update scale on mount

        // Optionally, update on window resize if the layout is responsive
        window.addEventListener('resize', updateScale);

        return () => {
            window.removeEventListener('resize', updateScale);
        };
    }, [originalSize.width]); // Recalculate when originalSize.width changes



    const handleBoxClick = (index, e) => {
        e.stopPropagation();  // Prevents event bubbling up
        if (index < 0 || index >= image.user_faces.length) {
            console.error(`Invalid index: ${index}`);
            setErrorMessage('An error occurred. Please try again.');
            return;
        }
        setEditableBoxIndex(index);
        const userFaceAtIndex = image.user_faces[index];
        setBoxText(userFaceAtIndex);
    };

    const handleBoxTextChange = (e) => {
        setBoxText(e.target.value);
    };

    const handlePlusButtonClick = async (e, index) => {
        e.stopPropagation();
        console.log('plus button clicked');
        if (boxText.trim() === '') {
            setErrorMessage('No name entered.');
            return;
        }

        try {
            const faceData = {
                inserted_id: image._id,
                anonymous_index: index,
                name: boxText,
            };

            const response = await axios.post(`${process.env.NEXT_PUBLIC_API_URL}/add-user-face`, faceData, {
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Bearer ${session.accessToken}`,
                },
            });

            if (response.status === 200) {
                setSuccessMessage('Name added successfully');
                // Update state or UI as needed
            } else {
                setErrorMessage('Failed to add name');
            }
        } catch (error) {
            console.log(error);
            setErrorMessage('Failed to add name');
        }

        setEditableBoxIndex(null);
    };

    const handleMouseDownOnPlusButton = (event) => {
        if (!event) {
            console.error('Invalid event');
            return;
        }
        event.preventDefault();
    };


    return (
        <div ref={overlayRef} style={{ position: 'relative' }}
             onMouseEnter={() => setIsMouseOver(true)}
             onMouseLeave={() => setIsMouseOver(false)}>
            {errorMessage && <ErrorWindow message={errorMessage} clearMessage={() => setErrorMessage(null)} />}
            {successMessage && <SuccessWindow message={successMessage} clearMessage={() => setSuccessMessage(null)} />}
            <Image
                src={image.image_url}
                alt={image.description}
                width={displayWidth}
                height={displayHeight}
                quality={100}
                className="rounded-lg"
            />
            {isMouseOver && (
                <div
                    className="absolute top-0 right-0 h-8 w-8 text-white text-3xl font-medium cursor-pointer"
                    onClick={() => {
                        setIsPlusClicked(!isPlusClicked);
                        setEnlargedImage(image.image_url);
                    }}
                    style={{ marginTop: '5px' }}
                >
                    <MagnifyingGlassIcon className="h-5 w-5 text-white" aria-hidden="true" />
                </div>
            )}
            {showHeartOverlay && (
                <div style={{
                    position: 'absolute',
                    top: '50%',
                    left: '50%',
                    transform: 'translate(-50%, -50%)',
                    zIndex: 1
                }}>
                    <HeartIcon className="h-10 w-10 text-gray-100 animate-pulse" />
                </div>
            )}
            {isMouseOver &&
                boxes.map((box, index) => (
                    <div
                        key={index}
                        style={{
                            position: 'absolute',
                            border: '2px solid red',
                            left: `${box[0] * scaleX}px`,
                            top: `${box[1] * scaleX}px`,
                            width: `${(box[2] - box[0]) * scaleX}px`,
                            height: `${(box[3] - box[1]) * scaleX}px`,
                            cursor: 'pointer',
                        }}
                        onClick={(e) => handleBoxClick(index, e)}
                    >
                        {editableBoxIndex === index && (
                            <div
                                style={{
                                    position: 'absolute',
                                    top: '102%',
                                    left: '0',
                                    right: '0',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    width: '100%',
                                }}
                            >
                                <input
                                    className="inline-block bg-blue-200 rounded-s-lg px-3 py-1 text-sm font-semibold text-gray-950 mr-2"
                                    type="text"
                                    value={boxText}
                                    onChange={isLoggedIn ? handleBoxTextChange : undefined} // Only allow change if logged in
                                    readOnly={!isLoggedIn}
                                    onBlur={() => setEditableBoxIndex(null)}
                                    autoFocus
                                    style={{
                                        flexGrow: 1,
                                        marginRight: '2px',
                                        border: '1px solid',
                                        width: 'auto',
                                        minWidth: '100px',
                                    }}
                                />
                                {isLoggedIn && (
                                    <button
                                        className="inline-block bg-blue-200 rounded-e-lg px-3 py-1 text-sm font-semibold text-gray-950 mr-2"
                                        onMouseDown={handleMouseDownOnPlusButton}
                                        onClick={(e) => handlePlusButtonClick(e, index)}
                                        style={{
                                            border: '1px solid',
                                            flexShrink: 0,
                                        }}
                                    >
                                        +
                                    </button>
                                )}
                            </div>
                        )}
                    </div>
                ))}
            {isPlusClicked && (
                <div
                    style={{
                        position: 'fixed',
                        top: 0,
                        left: 0,
                        width: '100%',
                        height: '100%',
                        backgroundColor: 'rgba(0, 0, 0, 0.5)',
                        display: 'flex',
                        justifyContent: 'center',
                        alignItems: 'center',
                        zIndex: 9999
                    }}
                    onClick={() => setIsPlusClicked(false)}
                >
                    <div
                        style={{
                            width: '95%',
                            height: '95%',
                            justifyContent: 'center',
                            alignItems: 'center',
                            overflow: 'auto',
                            scrollbarWidth: 'none',
                            msOverflowStyle: 'none'
                        }}
                    >
                        <div className="image-container1">
                            <Image
                                src={enlargedImage}
                                alt={image.description}
                                width={displayWidth * 1.2}
                                height={displayHeight * 1.2}
                                quality={100}
                                objectFit="contain"
                            />
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}