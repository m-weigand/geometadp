import { Arrayable } from "../types";
export declare function is_empty(array: Arrayable): boolean;
export declare function copy<T>(array: Arrayable<T>): Arrayable<T>;
export declare function splice<T>(array: Arrayable<T>, start: number, k?: number, ...items: T[]): Arrayable<T>;
export declare function head<T>(array: Arrayable<T>, n: number): Arrayable<T>;
export declare function insert<T>(array: Arrayable<T>, item: T, i: number): Arrayable<T>;
export declare function append<T>(array: Arrayable<T>, item: T): Arrayable<T>;
export declare function prepend<T>(array: Arrayable<T>, item: T): Arrayable<T>;
export declare function indexOf<T>(array: Arrayable<T>, item: T): number;
export declare function subselect<T>(array: Arrayable<T>, indices: Arrayable<number>): Arrayable<T>;
export declare function map(array: Float64Array, fn: (item: number, i: number, array: Float64Array) => number): Float64Array;
export declare function map(array: Float32Array, fn: (item: number, i: number, array: Float32Array) => number): Float32Array;
export declare function map<T, U>(array: T[], fn: (item: T, i: number, array: Arrayable<T>) => U): U[];
export declare function map<T, U>(array: Arrayable<T>, fn: (item: T, i: number, array: Arrayable<T>) => U): Arrayable<U>;
export declare function filter<T>(array: T[], pred: (item: T, i: number, array: Arrayable<T>) => boolean): T[];
export declare function filter<T>(array: Arrayable<T>, pred: (item: T, i: number, array: Arrayable<T>) => boolean): Arrayable<T>;
export declare function reduce<T>(array: Arrayable<T>, fn: (previous: T, current: T, index: number, array: Arrayable<T>) => T, initial?: T): T;
export declare function min(array: Arrayable<number>): number;
export declare function max(array: Arrayable<number>): number;
export declare function minmax(array: Arrayable<number>): [number, number];
export declare function min_by<T>(array: Arrayable<T>, key: (item: T) => number): T;
export declare function max_by<T>(array: Arrayable<T>, key: (item: T) => number): T;
export declare function sum(array: Arrayable<number>): number;
export declare function cumsum(array: number[]): number[];
export declare function cumsum(array: Arrayable<number>): Arrayable<number>;
export declare function every<T>(array: Arrayable<T>, predicate: (item: T) => boolean): boolean;
export declare function some<T>(array: Arrayable<T>, predicate: (item: T) => boolean): boolean;
export declare function index_of<T>(array: Arrayable<T>, value: T): number;
export declare const find_index: <T>(array: Arrayable<T>, predicate: (item: T) => boolean) => number;
export declare const find_last_index: <T>(array: Arrayable<T>, predicate: (item: T) => boolean) => number;
export declare function find<T>(array: Arrayable<T>, predicate: (item: T) => boolean): T | undefined;
export declare function find_last<T>(array: Arrayable<T>, predicate: (item: T) => boolean): T | undefined;
export declare function sorted_index<T>(array: Arrayable<T>, value: T): number;
export declare function bin_counts(data: Arrayable<number>, bin_edges: Arrayable<number>): Arrayable<number>;
export declare function interpolate(points: Arrayable<number>, x_values: Arrayable<number>, y_values: Arrayable<number>): Arrayable<number>;
export declare function left_edge_index(point: number, intervals: Arrayable<number>): number;
export declare function norm(array: Arrayable<number>, start: number, end: number): Arrayable<number>;
