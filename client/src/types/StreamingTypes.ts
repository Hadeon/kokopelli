export interface StationInfoProps<> {
    url: string;
    metadata: Record<string, string | undefined>; // Allows dynamic keys with string values
}
