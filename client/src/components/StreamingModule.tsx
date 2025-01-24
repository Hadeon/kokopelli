import React from "react";
import { StationInfoProps } from "../types/StreamingTypes";

function StreamingModule<T>({ StationInfo }: { StationInfo: StationInfoProps }) {
    const metadata = StationInfo.metadata || {};

    console.log("StationInfo:", StationInfo);

    // Helper function to capitalize metadata keys for readability
    const formatKey = (key: string) => {
        return key
            .replace(/_/g, " ") // Replace underscores with spaces
            .replace(/([a-z])([A-Z])/g, "$1 $2") // Add space before camel case
            .replace(/^./, (str) => str.toUpperCase()); // Capitalize first letter
    };

    return (
        <div className="streaming-module">
            <h2>Now listening to {metadata.StreamTitle || "Unknown Title"}</h2>
            <p>This is a placeholder for the current stream information.</p>

            {/* Dynamically display all metadata */}
            <div className="metadata">
                <h3>Stream Info</h3>
                {Object.keys(metadata).length > 0 ? (
                    <ul>
                        {Object.entries(metadata).map(([key, value]) => (
                            <li key={key}>
                                <strong>{formatKey(key)}:</strong> {value?.toString() || "N/A"}
                            </li>
                        ))}
                    </ul>
                ) : (
                    <p>No metadata available.</p>
                )}
            </div>
        </div>
    );
}

export default StreamingModule;
