// Maybe this whole thing could be implemented in rust and compiled to WASM, for faster performance

let pub_key = undefined
class RSA {
    constructor(pub_key){ // key should be fetched from /pubkey
        this.pub_key = this._parse_key(pub_key)
    }

    set_key(pub_key) {
        this.pub_key = this._parse_key(pub_key)
    }

    _toUTF8Array(str) {
        let utf8 = [];
        for (let i = 0; i < str.length; i++) {
            let charcode = str.charCodeAt(i);
            if (charcode < 0x80) utf8.push(charcode);
            else if (charcode < 0x800) {
                utf8.push(0xc0 | (charcode >> 6),
                    0x80 | (charcode & 0x3f));
            }
            else if (charcode < 0xd800 || charcode >= 0xe000) {
                utf8.push(0xe0 | (charcode >> 12),
                    0x80 | ((charcode >> 6) & 0x3f),
                    0x80 | (charcode & 0x3f));
            }
            // surrogate pair
            else {
                i++;
                // UTF-16 encodes 0x10000-0x10FFFF by
                // subtracting 0x10000 and splitting the
                // 20 bits of 0x0-0xFFFFF into two halves
                charcode = 0x10000 + (((charcode & 0x3ff) << 10)
                    | (str.charCodeAt(i) & 0x3ff));
                utf8.push(0xf0 | (charcode >> 18),
                    0x80 | ((charcode >> 12) & 0x3f),
                    0x80 | ((charcode >> 6) & 0x3f),
                    0x80 | (charcode & 0x3f));
            }
        }
        return utf8;
    }
    
    _Utf8ArrayToStr(array) {
        let out, i, len, c;
        let char2, char3;
    
        out = "";
        len = array.length;
        i = 0;
        while(i < len) {
        c = array[i++];
        switch(c >> 4)
        { 
          case 0: case 1: case 2: case 3: case 4: case 5: case 6: case 7:
            // 0xxxxxxx
            out += String.fromCharCode(c);
            break;
          case 12: case 13:
            // 110x xxxx   10xx xxxx
            char2 = array[i++];
            out += String.fromCharCode(((c & 0x1F) << 6) | (char2 & 0x3F));
            break;
          case 14:
            // 1110 xxxx  10xx xxxx  10xx xxxx
            char2 = array[i++];
            char3 = array[i++];
            out += String.fromCharCode(((c & 0x0F) << 12) |
                           ((char2 & 0x3F) << 6) |
                           ((char3 & 0x3F) << 0));
            break;
        }
        }
    
        return out;
    }
    
    _randomByte() {
        return crypto.getRandomValues(new Uint8Array(1))[0]
    }
    
    _randomBytes(n) {
        let r = []
        for (let i = 0; i < n; i++) {
            r.push(this._randomByte())
        }
        return r
    }
    
    _padRSAPkcs1(msg, target_len) {
        let maxMsgLength = target_len - 11
        let msgLength = msg.length
        if (msgLength > maxMsgLength) throw Error("Msg too big")
        let padding = []
        let padding_length = target_len - msgLength - 3
        while (padding.length < padding_length) {
            let neededBytes = padding_length - padding.length
            let new_padding = this._randomBytes(neededBytes + 8).filter(x => x != 0)
            padding = padding.concat(new_padding.slice(0, neededBytes))
        }
        if (padding.length != padding_length) throw Error("Padding doesn't match")
        return [0, 2].concat(padding).concat([0]).concat(msg) // 00 02 PADDING 00 MESSAGE
    }
    
    _bytearrayToNum(bytes) {
        let num = 0n
        for (let i = 0; i < bytes.length; i++) {
            num |= BigInt(bytes[i]) << BigInt(8 * (bytes.length - 1 - i))
        }
        return num
    }
    
    _numToBytearray(num) {
        let bytes = []
        let length = this._byte_size(num)
        for (let i = 0; i < length; i++) {
            bytes.push(Number((num & (255n << (8n * BigInt(length - 1 - i)))) >> (8n * BigInt(length - 1 - i))))
       }
        return bytes
    }
    
    _parse_key(key) {
        let spl = key.split(',')
        return {
            n: BigInt(spl[0]),
            e: BigInt(spl[1])
        }
    }
    
    _byte_size(n) {
        if (n == 0) return 1
        else return Math.ceil(n.toString(2).length / 8)
    }
    
    _encrypt_with_key(msg_str, key) { // Key must be the object generated from parse_key, 
        let msg = this._toUTF8Array(msg_str)
        let keylength = this._byte_size(key.n)
        msg = this._padRSAPkcs1(msg, keylength)
        let msg_bigint = this._bytearrayToNum(msg)
        let encr = this._encryptBigInt(msg_bigint, key)
        return this._numToBytearray(encr)
    }
    
    _modpow(x, y, p) { // What actually encrypts. Instead of doing pow and then mod, if you do it all at once, it's faster
        let res = 1n
        x = x % p
        if (x === 0n) return 0n
        while (y > 0n) {
            if ((y & 1n) == 1n) {
                res = (res * x) % p
            }
            y = y >> 1n
            x = (x * x) % p
        }
        return res
    }
    
    _encryptBigInt(num, key) {
        if (num < 0) throw Error('Only positive values can be encrypted')
        // if (num > n) throw Error('Number too big')
        return this._modpow(num, key.e, key.n)
    }
    
    encrypt(msg) {
        if(this.pub_key === undefined){
            //let res = await fetch('/pubkey')
            //pub_key = this._parse_key(await res.text())
            throw new Error('Pub key not set')
        }
        return this._encrypt_with_key(msg, this.pub_key)
    }

    sendBytes(data) { // test function, make sure input is bytearray
        fetch('/decrypt', {
            method: 'POST', // *GET, POST, PUT, DELETE, etc.
            mode: 'same-origin', // no-cors, *cors, same-origin
            cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
            credentials: 'same-origin', // include, *same-origin, omit
            headers: {
              'Content-Type': 'text/plain'
              // 'Content-Type': 'application/x-www-form-urlencoded',
            },
            redirect: 'follow', // manual, *follow, error
            referrerPolicy: 'no-referrer', // no-referrer, *no-referrer-when-downgrade, origin, origin-when-cross-origin, same-origin, strict-origin, strict-origin-when-cross-origin, unsafe-url
            body: this._bytearrayToNum(data).toString(16) // body data type must match "Content-Type" header
          })
    }
}