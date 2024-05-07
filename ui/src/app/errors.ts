export class ErrorBase<T extends string> extends Error {
    name: T;
    message: string;

    constructor(name: T, message: string) {
        super();
        this.name = name;
        this.message = message;
    }

}

export class FetchError extends ErrorBase<'FetchError'> {
    constructor(message: string) {
        super('FetchError', message);
    }
}