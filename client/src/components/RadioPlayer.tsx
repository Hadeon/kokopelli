import React, { useState, useEffect, Suspense, lazy } from "react";
import axios from "axios";

import { StationInfoProps } from "../types/StreamingTypes";

const RadioPlayer: React.FC = () => {
    const [stations, setStations] = useState<{ [key: string]: string }>({});
    const [search, setSearch] = useState("");
    const [newStation, setNewStation] = useState({ name: "", url: "" });
    const [currentStation, setCurrentStation] = useState<StationInfoProps | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [isPlaying, setIsPlaying] = useState(false);

    const StreamingModule = lazy(() => import("./StreamingModule"));

    // Fetch stations from the backend
    useEffect(() => {
        fetchStations();
    }, []);

    const fetchStations = async () => {
        setLoading(true);
        try {
            const response = await axios.get("http://127.0.0.1:5000/stations");
            setStations(response.data as any);
            setError(null);
        } catch {
            setError("Failed to load stations");
        } finally {
            setLoading(false);
        }
    };

    const handleSearch = async () => {
        setLoading(true);
        try {
            const response = await axios.get(`http://127.0.0.1:5000/stations?search=${search}`);
            setStations(response.data as any);
            setError(null);
        } catch {
            setError("Search failed");
        } finally {
            setLoading(false);
        }
    };

    const playStation = async (url: string) => {
        if (currentStation) {
            stopStation();
        }
        setLoading(true);
        try {
            const response = await axios.post("http://127.0.0.1:5000/play", { url });
            console.log("Play response:", response.data); // Debug response
            const { metadata } = response.data as any;
            setCurrentStation({ url, metadata });
            setIsPlaying(true);
            setError(null);
        } catch (error: any) {
            console.error("Play error:", error.response?.data || error.message);
            setError("Failed to play station");
        } finally {
            setLoading(false);
        }
    };
    

    const stopStation = async () => {
        setLoading(true);
        try {
            await axios.post("http://127.0.0.1:5000/stop");
            setCurrentStation(null);
            setIsPlaying(false);
            setError(null);
        } catch {
            setError("Failed to stop playback");
        } finally {
            setLoading(false);
        }
    };

    const addStation = async () => {
        if (!newStation.name || !newStation.url) {
            setError("Station name and URL are required");
            return;
        }
        setLoading(true);
        try {
            await axios.post("http://127.0.0.1:5000/stations", newStation);
            setNewStation({ name: "", url: "" });
            fetchStations();
            setError(null);
        } catch {
            setError("Failed to add station");
        } finally {
            setLoading(false);
        }
    };

    const deleteStation = async (name: string) => {
        setLoading(true);
        try {
            await axios.delete(`http://127.0.0.1:5000/stations/${encodeURIComponent(name)}`);
            fetchStations();
            setError(null);
        } catch {
            setError("Failed to delete station");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ maxWidth: "600px", margin: "0 auto", padding: "1rem" }}>
            <h1>Radio Player</h1>
            {error && <p style={{ color: "red" }}>{error}</p>}
            {loading && <p>Loading...</p>}

            <div>
                <input
                    type="text"
                    placeholder="Search stations"
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                />
                <button onClick={handleSearch}>Search</button>
            </div>

            <ul>
                {Object.entries(stations).map(([name, url]) => (
                    <li key={name} style={{ margin: "0.5rem 0" }}>
                        <strong>{name}</strong>
                        <button onClick={() => playStation(url)} style={{ marginLeft: "0.5rem" }}>
                            Play
                        </button>
                        <button onClick={() => deleteStation(name)} style={{ marginLeft: "0.5rem" }}>
                            Delete
                        </button>
                    </li>
                ))}
            </ul>

            {currentStation && (
                <div>
                    {isPlaying && (
                        <Suspense fallback={<div>Loading...</div>}>
                            <StreamingModule StationInfo={currentStation} />
                        </Suspense>
                    )}
                    <button onClick={stopStation}>Stop</button>
                </div>
            )}

            <h2>Add New Station</h2>
            <div>
                <input
                    type="text"
                    placeholder="Station Name"
                    value={newStation.name}
                    onChange={(e) => setNewStation({ ...newStation, name: e.target.value })}
                />
                <input
                    type="text"
                    placeholder="Station URL"
                    value={newStation.url}
                    onChange={(e) => setNewStation({ ...newStation, url: e.target.value })}
                />
                <button onClick={addStation}>Add</button>
            </div>
        </div>
    );
};

export default RadioPlayer;