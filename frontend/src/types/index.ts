export interface CompanyItem {
    id: number;
    company_id: number;
    identifier: string;
    ean13?: string;
    name: string;
    unit_id?: number;
    rrprice: number;
    microwholeprice: number;
    mediumwholeprice: number;
    maxwholeprice: number;
    stock: number;
  }
  
  export interface Company {
    id: number;
    name: string;
    inn: string;
  }