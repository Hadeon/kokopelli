import React, { useState, useEffect } from "react";
import axios from "axios";

const RadioPlayer: React.FC = () => {
    const [stations, setStations] = useState<{ [key: string]: string }>({});
    const [search, setSearch] = useState("");
    const [currentStation, setCurrentStation] = useState<string | null>(null);

    useEffect(() => {
        // Fetch stations from the backend
        axios.get("http://127.0.0.1:5000/stations").then((response) => {
            setStations(response.data);
        });
    }, []);

    const handleSearch = () => {
        axios.get(`http://127.0.0.1:5000/stations?search=${search}`).then((response) => {
            setStations(response.data);
        });
    };

    const playStation = (url: string) => {
        if(currentStation) {
            stopStation();
        }
        axios.post("http://127.0.0.1:5000/play", { url }).then(() => {
            setCurrentStation(url);
        });
    };

    const stopStation = () => {
        axios.post("http://127.0.0.1:5000/stop").then(() => {
            setCurrentStation(null);
        });
    };

    return (
        <div>
            <h1>Radio Player</h1>
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
                    <li key={name}>
                        {name}
                        <button onClick={() => playStation(url)}>Play</button>
                    </li>
                ))}
            </ul>
            {currentStation && (
                <div>
                    <p>Now Playing: {currentStation}</p>
                    <button onClick={stopStation}>Stop</button>
                </div>
            )}
        </div>
    );
};

export default RadioPlayer;
