/* 
Transpiled to Python: 

https://pypi.org/project/javascripthon

Required several edits after transpilation. E.g. endswith --> endsWith.
*/


var _pj;
function _pj_snippets(container) {
    function _assert(comp, msg) {
        function PJAssertionError(message) {
            this.name = "PJAssertionError";
            this.message = (message || "Custom error PJAssertionError");
            if (((typeof Error.captureStackTrace) === "function")) {
                Error.captureStackTrace(this, this.constructor);
            } else {
                this.stack = new Error(message).stack;
            }
        }
        PJAssertionError.prototype = Object.create(Error.prototype);
        PJAssertionError.prototype.constructor = PJAssertionError;
        msg = (msg || "Assertion failed.");
        if ((!comp)) {
            throw new PJAssertionError(msg);
        }
    }
    container["_assert"] = _assert;
    return container;
}
_pj = {};
_pj_snippets(_pj);
function TransportError(message) {
    this.name = "TransportError";
    this.message = (message || "Custom error TransportError");
    if (((typeof Error.captureStackTrace) === "function")) {
        Error.captureStackTrace(this, this.constructor);
    } else {
        this.stack = new Error(message).stack;
    }
}
TransportError.prototype = Object.create(Error.prototype);
TransportError.prototype.constructor = TransportError;
export class SerialTransport {
    constructor(serial) {
        this.use_raw_paste = true;
        this.serial = serial;
    }
    close() {
        this.serial.close();
    }
    async read_until(min_num_bytes, ending, timeout = 10, data_consumer = null) {
        var data, new_data, timeout_count;
        _pj._assert(((data_consumer === null) || (ending.length === 1)), null);
        data = await this.serial.read(min_num_bytes);
        if (data_consumer) {
            data_consumer(data);
        }
        timeout_count = 0;
        while (true) {
            if (data.endsWith(ending)) {
                break;
            } else {
                if ((this.serial.inWaiting() > 0)) {
                    new_data = await this.serial.read(1);
                    if (data_consumer) {
                        data_consumer(new_data);
                        data = new_data;
                    } else {
                        data = (data + new_data);
                    }
                    timeout_count = 0;
                } else {
                    timeout_count += 1;
                    if (((timeout !== null) && (timeout_count >= (100 * timeout)))) {
                        break;
                    }
                }
            }
        }
        return data;
    }

    async enter_raw_repl(soft_reset = true) {
        var data, n;
        await this.serial.write("\r\u0003\u0003");
        n = this.serial.inWaiting();
        while ((n > 0)) {
            await this.serial.read(n);
            n = this.serial.inWaiting();
        }
        await this.serial.write("\r\u0001");
        if (soft_reset) {
            data = await this.read_until(1, "raw REPL; CTRL-B to exit\r\n>");
            if ((!data.endsWith("raw REPL; CTRL-B to exit\r\n>"))) {
                throw new TransportError("could not enter raw repl");
            }
            await this.serial.write("\u0004");
            data = await this.read_until(1, "soft reboot\r\n");
            if ((!data.endsWith("soft reboot\r\n"))) {
                throw new TransportError("could not enter raw repl");
            }
        }
        data = await this.read_until(1, "raw REPL; CTRL-B to exit\r\n");
        if ((!data.endsWith("raw REPL; CTRL-B to exit\r\n"))) {
            throw new TransportError("could not enter raw repl");
        }
        this.in_raw_repl = true;
    }
    async exit_raw_repl() {
        await this.serial.write("\r\u0002");
        this.in_raw_repl = false;
    }
    async follow(timeout, data_consumer = null) {
        var data, data_err;
        data = await this.read_until(1, "\u0004", { "timeout": timeout, "data_consumer": data_consumer });
        if ((!data.endsWith("\u0004"))) {
            throw new TransportError("timeout waiting for first EOF reception");
        }
        data = data.slice(0, (- 1));
        data_err = await this.read_until(1, "\u0004", { "timeout": timeout });
        if ((!data_err.endsWith("\u0004"))) {
            throw new TransportError("timeout waiting for second EOF reception");
        }
        data_err = data_err.slice(0, (- 1));
        return [data, data_err];
    }
    async raw_paste_write(command_bytes) {
        var b, data, i, window_remain, window_size;
        window_size = await this.serial.readUint16(1);
        window_size = window_size[0];
        window_remain = window_size;
        i = 0;
        while ((i < command_bytes.length)) {
            while (((window_remain === 0) || this.serial.inWaiting())) {
                data = await this.serial.readUint8(1);
                data = data[0];
                if (data === 1) {
                    window_remain += window_size;
                } else {
                    if (data === 4) {
                        await this.serial.write("\u0004");
                        return;
                    } else {
                        throw new TransportError("unexpected read during raw paste: {}".format(data));
                    }
                }
            }

            b = command_bytes.slice(i, Math.min((i + window_remain), command_bytes.length));
            await this.serial.write(b);
            window_remain -= b.length;
            i += b.length;
        }
        await this.serial.write("\u0004");
        data = await this.read_until(1, "\u0004");
        if ((!data.endsWith("\u0004"))) {
            throw new TransportError("could not complete raw paste: {}".format(data));
        }
    }
    async exec_raw_no_follow(command) {
        const command_bytes = command;
        var data;
        data = await this.read_until(1, ">");
        if ((!data.endsWith(">"))) {
            throw new TransportError("could not enter raw repl");
        }
        if (this.use_raw_paste) {
            await this.serial.write("\u0005A\u0001");
            data = await this.serial.read(2);
            if ((data === "R\u0000")) {
                // Device understood raw-paste command but doesn't support it.
            } else {
                if ((data === "R\u0001")) {
                    // Device supports raw-paste mode, write out the command using this mode.
                    return this.raw_paste_write(command_bytes);
                } else {
                    // Device doesn't support raw-paste, fall back to normal raw REPL.
                    data = await this.read_until(1, "w REPL; CTRL-B to exit\r\n>");
                    if ((!data.endsWith("w REPL; CTRL-B to exit\r\n>"))) {
                        throw new TransportError("could not enter raw repl");
                    }
                }
            }
            this.use_raw_paste = false;
        }
        for (var i = 0, _pj_a = command_bytes.length; (i < _pj_a); i += 256) {
            await this.serial.write(command_bytes.slice(i, Math.min((i + 256), command_bytes.length)));
        }
        await this.serial.write("\u0004");
        data = await this.serial.read(2);
        if ((data !== "OK")) {
            throw new TransportError(("could not exec command (response: %r)" % data));
        }
    }
    async exec_raw(command, timeout = 10, data_consumer = null) {
        await this.exec_raw_no_follow(command);
        return await this.follow(timeout, data_consumer);
    }
    async eval(expression) {
        var ret;
        ret = await this.exec("print({})".format(expression));
        ret = ret.strip();
        return ret;
    }
    async exec(command, data_consumer = null) {
        var ret, ret_err;
        [ret, ret_err] = await this.exec_raw(command, { "data_consumer": data_consumer });
        if (ret_err) {
            throw new TransportError("exception", ret, ret_err);
        }
        return ret;
    }

}
