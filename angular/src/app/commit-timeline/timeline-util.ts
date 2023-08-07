export class TimelineUtil {
    static padZero(x: number): string {
        return `${x > 9 ? '' : '0'}${x}`
    }

    static shuffleArray<T>(array: T[]): T[] {
        var m = array.length, t, i;
        
        while (m) {    
            i = Math.floor(Math.random() * m--);
            t = array[m];
            array[m] = array[i];
            array[i] = t;
        }
        
        return array;
    }  
}