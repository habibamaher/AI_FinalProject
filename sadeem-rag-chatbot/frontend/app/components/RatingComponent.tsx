import React, { useState } from 'react';
import { Star } from 'lucide-react';

interface RatingComponentProps {
    sessionId: string;
    onRatingSubmitted: () => void;
}

const RatingComponent: React.FC<RatingComponentProps> = ({ sessionId, onRatingSubmitted }) => {
    const [rating, setRating] = useState<number>(0);
    const [hoveredRating, setHoveredRating] = useState<number>(0);
    const [submitted, setSubmitted] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);

    const handleRatingSubmit = async (selectedRating: number) => {
        setRating(selectedRating);
        setError(null);

        try {
            const response = await fetch(`http://localhost:5000/api/session/${sessionId}/rating`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ rating: selectedRating }),
            });

            if (response.ok) {
                setSubmitted(true);
                setTimeout(() => {
                    onRatingSubmitted();
                }, 2000);
            } else {
                setError('Failed to submit rating. Please try again.');
            }
        } catch (err) {
            setError('An error occurred. Please try again.');
        }
    };

    if (submitted) {
        return (
            <div className="flex flex-col items-center justify-center p-4 bg-gray-800/50 rounded-lg border border-green-500/30 animate-fade-in">
                <p className="text-green-400 font-medium mb-2">Thank you for your feedback!</p>
                <div className="flex gap-1">
                    {[1, 2, 3, 4, 5].map((star) => (
                        <Star key={star} size={20} className="fill-green-400 text-green-400" />
                    ))}
                </div>
            </div>
        );
    }

    return (
        <div className="flex flex-col items-center justify-center p-4 bg-gray-800/50 rounded-lg border border-gray-700 animate-fade-in mt-2">
            <p className="text-gray-300 font-medium mb-3">How helpful was this conversation?</p>

            <div className="flex gap-2 mb-2">
                {[1, 2, 3, 4, 5].map((star) => (
                    <button
                        key={star}
                        className="transition-transform hover:scale-110 focus:outline-none"
                        onMouseEnter={() => setHoveredRating(star)}
                        onMouseLeave={() => setHoveredRating(0)}
                        onClick={() => handleRatingSubmit(star)}
                    >
                        <Star
                            size={28}
                            className={`${star <= (hoveredRating || rating)
                                    ? 'fill-yellow-400 text-yellow-400'
                                    : 'text-gray-500'
                                } transition-colors duration-200`}
                        />
                    </button>
                ))}
            </div>

            {error && <p className="text-red-400 text-sm mt-2">{error}</p>}
        </div>
    );
};

export default RatingComponent;
