import http from 'k6/http';
import { sleep } from 'k6';

export default function () { 
  http.get('https://www.wannadrinks.com/');
  sleep(1);
}

export const options = {
  vus: 100,
  duration: '3m',
};