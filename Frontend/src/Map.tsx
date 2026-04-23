import { useEffect, useState } from "react";
import { MapContainer, TileLayer, ImageOverlay } from "react-leaflet";
import type { LatLngBoundsExpression } from "leaflet";
import 'leaflet/dist/leaflet.css';

interface MapProperties {
    type: "pre" | "post"
}

type GeotransformEntry = [[number, number, number, number, number, number], string]
type GeotransformJSON = Record<string, GeotransformEntry>

const S3_IMGS = "https://amzn-santa-rosa-wildfire-images.s3.us-east-1.amazonaws.com/datatsetCapstone"
const IMG_SIZE = 1024

//This is where the maps images are added. Its getting the edges of each image and calculating it.
function getBounds(geotransform: [number, number, number, number, number, number]): LatLngBoundsExpression {

    const padding = 0.00

    const [long, pixelW, , lat, , pixelH] = geotransform
    const north = lat
    const south = lat + (pixelH * (IMG_SIZE)) + padding
    const west = long
    const east = long + (pixelW * (IMG_SIZE)) - padding
    return [[south, west], [north, east]]
}

export default function Map({type}: MapProperties){
    const [overlay, setOverlay] = useState<{ url: string; bounds: LatLngBoundsExpression} []>([])

    useEffect(() => {
        fetch("../public/santa_rose_geotransform.json")
        .then (res => res.json())
        .then((data: GeotransformJSON) => {
            const suffix = type === "pre" ? "pre_disaster" : "post_disaster"

            const filtered = Object.entries(data)
                .filter(([filename]) => filename.includes(suffix))
                .map(([filename, [geotransform]]) => ({
                    url: `${S3_IMGS}/${filename}`,
                    bounds: getBounds(geotransform)
                }))
            setOverlay(filtered)
        })
    }, [type])

    return (
        <MapContainer
            center = {[38.43528784609693, -122.71303705013497]}
            zoom = {13}
            style = {{height: "100%", width: "100%"}}
        >
            <TileLayer
                url = "https://api.maptiler.com/maps/satellite-v4/{z}/{x}/{y}.jpg?key=g5cvX3fWQLMVoSF0kway"
                tileSize = {512}
                zoomOffset= {-1}
                opacity={0.5}
                attribution="© MapTiler © OpenStreetMap contributors"
            />
            {overlay.map(({url, bounds}) => (
                <ImageOverlay
                    key={url}
                    url={url}
                    bounds={bounds}
                    opacity={1.0}
                />
            ))}
        </MapContainer>
    )
}