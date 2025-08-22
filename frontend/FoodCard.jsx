import React from "react";
import { Link } from "react-router-dom";
import { Star, Info } from "lucide-react";

const FoodCard = ({ food }) => {
    if (!food) return null;

    const {
        id,
        name,
        description,
        price,
        category,
        average_rating,
        rating_count,
        main_image,
    } = food;

    // Format price to IDR currency
    const formattedPrice = new Intl.NumberFormat("id-ID", {
        style: "currency",
        currency: "IDR",
        minimumFractionDigits: 0,
    }).format(price);

    // Default image in case main_image is not available
    const imageUrl =
        main_image?.image_url ||
        "https://via.placeholder.com/300x200?text=No+Image";

    return (
        <div className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300">
            <div className="relative">
                <img
                    src={imageUrl}
                    alt={name}
                    className="w-full h-48 object-cover"
                    onError={(e) => {
                        e.target.src =
                            "https://via.placeholder.com/300x200?text=Error+Loading+Image";
                    }}
                />
                <div className="absolute top-2 right-2 bg-white px-2 py-1 rounded-full text-sm font-semibold">
                    {category}
                </div>
            </div>

            <div className="p-4">
                <h3 className="text-lg font-bold text-gray-800 mb-1 truncate">
                    {name}
                </h3>

                <div className="flex items-center text-sm text-gray-600 mb-2">
                    <div className="flex items-center mr-3">
                        <Star
                            className={`h-4 w-4 ${
                                average_rating > 0
                                    ? "text-yellow-500"
                                    : "text-gray-400"
                            }`}
                        />
                        <span className="ml-1">
                            {average_rating?.toFixed(1) || "N/A"}
                        </span>
                    </div>
                    <span>({rating_count || 0} reviews)</span>
                </div>

                <p className="text-gray-600 text-sm mb-3 line-clamp-2">
                    {description}
                </p>

                <div className="flex items-center justify-between">
                    <div className="text-lg font-bold text-indigo-600">
                        {formattedPrice}
                    </div>
                    <Link
                        to={`/food/${id}`}
                        className="bg-indigo-600 hover:bg-indigo-700 text-white px-3 py-1 rounded-md flex items-center text-sm"
                    >
                        <Info className="h-4 w-4 mr-1" />
                        Details
                    </Link>
                </div>
            </div>
        </div>
    );
};

export default FoodCard;
