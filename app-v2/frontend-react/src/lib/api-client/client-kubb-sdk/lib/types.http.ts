import * as OperationsTypes from "./generated/output-ts";
import { settingsSchema } from './generated/output-zod/settingsSchema';

// ========= API Operations =========

export type { OperationsTypes };

// ========= Playlist =========

export type PlaylistRaw = OperationsTypes.PlaylistRaw;
export type DerivedTrack = OperationsTypes.TrackDerived;
export type DerivedPlaylist = OperationsTypes.PlaylistDerived;

// ========= Settings =========

export const schemaSettings = settingsSchema;
export type Settings = OperationsTypes.Settings;

